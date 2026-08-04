"""Serializers del bloque alumnos — HU-04 (Seccion + Alumno).

Las reglas de dominio que el modelo a propósito no impone viven acá (mismo
criterio que el spike de login: la validación es del serializer, no del .save()).
El serializer de `Vinculo` llega en HU-05.
"""

from rest_framework import serializers

from .models import Alumno, Seccion


class SeccionSerializer(serializers.ModelSerializer):
    nivel_display = serializers.CharField(source="get_nivel_display", read_only=True)
    turno_display = serializers.CharField(source="get_turno_display", read_only=True)

    class Meta:
        model = Seccion
        fields = [
            "id", "nivel", "nivel_display",
            "nombre", "turno", "turno_display", "activa",
        ]


class AlumnoSerializer(serializers.ModelSerializer):
    # `seccion` (PK) es escribible; `seccion_detalle` es el objeto anidado de solo
    # lectura, para no tener que pegar una segunda llamada al listar.
    seccion_detalle = SeccionSerializer(source="seccion", read_only=True)
    turno = serializers.SerializerMethodField()

    class Meta:
        model = Alumno
        fields = [
            "id", "nombre", "apellido", "dni", "domicilio",
            "seccion", "seccion_detalle", "turno", "activo",
        ]

    def get_turno(self, obj):
        # Derivado de la sección (property del modelo); None si no tiene sección.
        return obj.turno
