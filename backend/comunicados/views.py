"""
Vistas de la app `comunicados`.

- `ComunicadoViewSet`: CRUD para el emisor (admin/autoridad/docente). Al crear,
  valida el ALCANCE (destino ⊆ alcance del emisor, BK26) ANTES de persistir:
  arma un `Comunicado` transitorio y le pregunta `destino_en_alcance`; si no
  cae, 403 y no se guarda nada ni se dispara el fan-out. Recién con el alcance
  OK sella el `emisor` con el token, guarda y genera las entregas. La misma
  validación cubre el update (para que no se pueda mover el destino fuera de
  alcance por PATCH después de emitir).
- `MiBandejaViewSet`: la bandeja del familiar, de solo lectura. Filtra por el
  token (`request.user`), NUNCA por un id de la URL — mismo principio de "lo mío"
  que `MisAlumnosViewSet`. El acuse (RF09/RF10) es la acción `acusar/`.
"""

from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Comunicado, EntregaComunicado
from .permissions import EmiteAdminAutoridadODocente
from .serializers import ComunicadoSerializer, EntregaComunicadoSerializer


class ComunicadoViewSet(viewsets.ModelViewSet):
    queryset = Comunicado.objects.select_related(
        "emisor", "seccion", "alumno", "grupo"
    ).all()
    serializer_class = ComunicadoSerializer
    permission_classes = [EmiteAdminAutoridadODocente]

    def _verificar_emision(self, serializer):
        """Row-level auth de la escritura, DOS compuertas ortogonales sobre una
        instancia transitoria (antes de guardar; nada persiste si alguna falla):
        1. VERTICAL: el destino debe caer en el alcance del emisor (7a/S06).
        2. FUNCIONAL: la categoria debe estar permitida para su cargo (7b, RF25).
        Cada una con su 403 propio. La coherencia de campos ya paso en el
        serializer (400); esto es autorizacion."""
        emisor = self.request.user
        tentativo = Comunicado(emisor=emisor, **serializer.validated_data)
        if not tentativo.destino_en_alcance(emisor):
            raise PermissionDenied(
                "El destino elegido esta fuera de tu alcance de emision."
            )
        if not tentativo.categoria_permitida(emisor):
            raise PermissionDenied(
                "No podes emitir comunicados de esa categoria."
            )

    def perform_create(self, serializer):
        self._verificar_emision(serializer)
        # Atomico: o queda el comunicado CON sus entregas, o no queda nada. Sin
        # esto, si generar_entregas() falla, quedaria un broadcast huerfano
        # (persistido pero sin destinatarios). Mismo criterio que el create de
        # mensajeria.
        with transaction.atomic():
            comunicado = serializer.save(emisor=self.request.user)
            comunicado.generar_entregas()

    def perform_update(self, serializer):
        self._verificar_emision(serializer)
        serializer.save()

    @action(detail=True, methods=["get"], url_path="entregas")
    def entregas(self, request, pk=None):
        """Estado de acuse del comunicado, entrega por entrega."""
        comunicado = self.get_object()
        qs = comunicado.entregas.select_related("familiar", "alumno")
        return Response(EntregaComunicadoSerializer(qs, many=True).data)


class MiBandejaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EntregaComunicadoSerializer

    def get_queryset(self):
        return EntregaComunicado.objects.filter(
            familiar=self.request.user
        ).select_related("comunicado", "alumno")

    @action(detail=True, methods=["post"], url_path="acusar")
    def acusar(self, request, pk=None):
        entrega = self.get_object()  # get_queryset ya limita a las del token
        if not entrega.comunicado.requiere_acuse:
            return Response(
                {"detail": "Este comunicado no requiere acuse."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Idempotente: si ya estaba acusado, se conserva el primer acuse.
        if entrega.acusado_en is None:
            entrega.acusado_en = timezone.now()
            entrega.save(update_fields=["acusado_en"])
        return Response(EntregaComunicadoSerializer(entrega).data)