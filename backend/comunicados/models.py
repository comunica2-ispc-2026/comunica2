"""
App `comunicados` -- circulares y acuse de recibo de Comunica2 (fase 1).

Cubre RF08 (emitir comunicados) y RF09/RF10 (acuse de recibo con fecha/hora).
Backlog BK08/BK09.

Diseno fase-1:
- Destinos INDIVIDUAL (un alumno) y SECCION (una seccion). Los destinos por
  nivel/turno/grupo y el scoping por alcance del emisor llegan en fase 2.
- Bandeja por ENTREGA MATERIALIZADA (fan-out on write): al emitir, una fila de
  entrega por cada familiar vinculado a cada alumno del destino. La bandeja es un
  SELECT directo; "quien acuso / quien no" es una agregacion sobre esa tabla.
- Grano de la entrega = (comunicado, familiar, alumno): un familiar con varios
  hijos recibe y acusa por CADA hijo.
- Emision por ROL (admin/autoridad/docente) -> vive en permissions.py.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from alumnos.models import Alumno, Seccion, Vinculo

# Campos localizadores posibles en fase 1. Por cada tipo de destino
# (REQUERIDOS_POR_TIPO), cuales deben venir seteados; el resto debe quedar nulo.
_LOCALIZADORES = ("alumno", "seccion")


class Comunicado(models.Model):
    class TipoDestino(models.TextChoices):
        INDIVIDUAL = "INDIVIDUAL", "Un alumno"
        SECCION = "SECCION", "Una seccion"

    REQUERIDOS_POR_TIPO = {
        TipoDestino.INDIVIDUAL: {"alumno"},
        TipoDestino.SECCION: {"seccion"},
    }

    emisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="comunicados_emitidos",
    )
    titulo = models.CharField(max_length=150)
    cuerpo = models.TextField()

    tipo_destino = models.CharField(
        max_length=10, choices=TipoDestino.choices, default=TipoDestino.SECCION
    )

    # Localizadores. Cual va seteado depende de tipo_destino; la coherencia la
    # garantiza clean(). Ambos nullables. PROTECT en las FK: no se borra un
    # alumno/seccion con comunicados dirigidos.
    alumno = models.ForeignKey(
        "alumnos.Alumno", on_delete=models.PROTECT,
        related_name="comunicados_individuales", null=True, blank=True,
    )
    seccion = models.ForeignKey(
        "alumnos.Seccion", on_delete=models.PROTECT,
        related_name="comunicados", null=True, blank=True,
    )

    requiere_acuse = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.titulo} -> {self.descripcion_destino()}"

    # --- coherencia tipo <-> localizadores -----------------------------------

    @classmethod
    def errores_coherencia(cls, tipo, *, alumno, seccion):
        """Dict {campo: mensaje} con las incoherencias tipo<->localizadores.
        Vacio = coherente. Estatico a proposito: lo usan el modelo (clean) y el
        serializer, sin duplicar la regla. Los valores son 'presente o no'."""
        try:
            requeridos = cls.REQUERIDOS_POR_TIPO[tipo]
        except KeyError:
            return {"tipo_destino": "Tipo de destino desconocido."}
        presentes = {"alumno": alumno, "seccion": seccion}
        display = cls.TipoDestino(tipo).label
        errores = {}
        for campo in _LOCALIZADORES:
            valor = presentes[campo] or None
            if campo in requeridos and not valor:
                errores[campo] = f"Requerido para un comunicado de tipo '{display}'."
            elif campo not in requeridos and valor:
                errores[campo] = f"No corresponde para un comunicado de tipo '{display}'."
        return errores

    def clean(self):
        """La API la ejerce (400 via serializer); el .save() directo no corre
        validators (mismo criterio que el dni en alumnos)."""
        errores = self.errores_coherencia(
            self.tipo_destino, alumno=self.alumno_id, seccion=self.seccion_id
        )
        if errores:
            raise ValidationError(errores)

    # --- destino -> secciones / alumnos --------------------------------------

    def _secciones_de_destino(self):
        """Secciones activas que abarca el destino (solo SECCION en fase 1).
        Vacio para INDIVIDUAL, que resuelve su alumno por otra via."""
        if self.tipo_destino == self.TipoDestino.SECCION:
            return Seccion.objects.filter(pk=self.seccion_id, activa=True)
        return Seccion.objects.none()

    def descripcion_destino(self):
        T = self.TipoDestino
        if self.tipo_destino == T.INDIVIDUAL:
            return str(self.alumno) if self.alumno_id else "un alumno"
        if self.tipo_destino == T.SECCION:
            return str(self.seccion) if self.seccion_id else "una seccion"
        return "destino"

    def alumnos_destinatarios(self):
        """Alumnos activos alcanzados segun tipo_destino (INDIVIDUAL/SECCION)."""
        qs = Alumno.objects.filter(activo=True)
        if self.tipo_destino == self.TipoDestino.INDIVIDUAL:
            return qs.filter(pk=self.alumno_id)
        return qs.filter(seccion__in=self._secciones_de_destino())

    # --- fan-out on write -----------------------------------------------------

    def generar_entregas(self):
        """Fan-out on write: una entrega por cada Vinculo activo a cada alumno
        del destino. Idempotente (`ignore_conflicts` sobre el unique)."""
        vinculos = Vinculo.objects.filter(
            alumno__in=self.alumnos_destinatarios(), activo=True
        ).select_related("usuario", "alumno")
        entregas = [
            EntregaComunicado(comunicado=self, familiar=v.usuario, alumno=v.alumno)
            for v in vinculos
        ]
        return EntregaComunicado.objects.bulk_create(entregas, ignore_conflicts=True)


class EntregaComunicado(models.Model):
    """Una fila por (comunicado, familiar, alumno). Es la bandeja y el acuse a la
    vez: que exista = fue entregado (RF08); `acusado_en` no nulo = acusado, con
    su fecha/hora (RF09/RF10)."""

    comunicado = models.ForeignKey(
        Comunicado, on_delete=models.CASCADE, related_name="entregas"
    )
    familiar = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entregas_recibidas",
    )
    alumno = models.ForeignKey(
        Alumno, on_delete=models.CASCADE, related_name="entregas"
    )

    entregado_en = models.DateTimeField(auto_now_add=True)
    acusado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-entregado_en"]
        constraints = [
            models.UniqueConstraint(
                fields=["comunicado", "familiar", "alumno"],
                name="uniq_entrega_comunicado_familiar_alumno",
            )
        ]

    @property
    def acusado(self):
        return self.acusado_en is not None

    def __str__(self):
        estado = "acusado" if self.acusado else "pendiente"
        return f"{self.comunicado.titulo} - {self.familiar} / {self.alumno} ({estado})"
