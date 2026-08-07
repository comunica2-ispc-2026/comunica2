"""Serializers de `institucion` — administracion del alcance (admin-only).

Reglas de dominio que el modelo dejo permisivas a proposito (mismo criterio que
VinculoSerializer.validate_usuario): se ejercen ACA.

- AsignacionDocente.docente  -> debe tener rol DOCENTE.
- AlcanceAutoridad.autoridad -> debe tener rol AUTORIDAD.
- AlcanceGrupo.autoridad     -> debe tener rol AUTORIDAD.

Coherencia cargo<->tipo de alcance (director/vice=turno NULL, preceptor=turno,
tesorero=grupos): se deja PERMISIVA a proposito. El resolver ya contempla que un
mismo usuario tenga ambas fuentes de alcance; no se fuerza el mapeo aca.

Patron de lectura: al PK escribible se le suma un `*_detalle` de solo lectura
(igual que seccion/seccion_detalle en AlumnoSerializer), para no pegar una
segunda llamada al listar.
"""

from rest_framework import serializers

from alumnos.serializers import SeccionSerializer
from usuarios.models import Usuario

from .models import (
    AlcanceAutoridad,
    AlcanceGrupo,
    AsignacionDocente,
    GrupoPersonalizado,
)


def _validar_rol(value, rol_esperado, etiqueta):
    if value.rol != rol_esperado:
        raise serializers.ValidationError(
            f"El usuario debe tener rol {etiqueta}."
        )
    return value


class AsignacionDocenteSerializer(serializers.ModelSerializer):
    seccion_detalle = SeccionSerializer(source="seccion", read_only=True)

    class Meta:
        model = AsignacionDocente
        fields = ["id", "docente", "seccion", "seccion_detalle", "activa"]

    def validate_docente(self, value):
        return _validar_rol(value, Usuario.Rol.DOCENTE, "DOCENTE")


class AlcanceAutoridadSerializer(serializers.ModelSerializer):
    nivel_display = serializers.CharField(source="get_nivel_display", read_only=True)
    turno_display = serializers.CharField(source="get_turno_display", read_only=True)

    class Meta:
        model = AlcanceAutoridad
        fields = [
            "id", "autoridad",
            "nivel", "nivel_display",
            "turno", "turno_display",
        ]

    def validate_autoridad(self, value):
        return _validar_rol(value, Usuario.Rol.AUTORIDAD, "AUTORIDAD")


class GrupoPersonalizadoSerializer(serializers.ModelSerializer):
    secciones_detalle = SeccionSerializer(source="secciones", many=True, read_only=True)

    class Meta:
        model = GrupoPersonalizado
        fields = ["id", "nombre", "secciones", "secciones_detalle", "activo"]


class AlcanceGrupoSerializer(serializers.ModelSerializer):
    grupo_detalle = GrupoPersonalizadoSerializer(source="grupo", read_only=True)

    class Meta:
        model = AlcanceGrupo
        fields = ["id", "autoridad", "grupo", "grupo_detalle"]

    def validate_autoridad(self, value):
        return _validar_rol(value, Usuario.Rol.AUTORIDAD, "AUTORIDAD")
