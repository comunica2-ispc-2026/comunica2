"""
Serializers de la app `comunicados` (fase 1).

- `ComunicadoSerializer`: el emisor (admin/autoridad/docente). Trae el conteo de
  acuse (destinatarios / acusados) sin query aparte. La coherencia
  tipo_destino<->localizadores se delega en `Comunicado.errores_coherencia`
  (misma regla que el `clean()` del modelo, sin duplicarla) y se devuelve como 400.
- `EntregaComunicadoSerializer`: la vista de estado del emisor y (en HU-08) la
  bandeja del familiar. De solo lectura; el acuse va por una accion, no por PATCH.
"""

from rest_framework import serializers

from .models import Comunicado, EntregaComunicado


class ComunicadoSerializer(serializers.ModelSerializer):
    emisor_nombre = serializers.StringRelatedField(source="emisor", read_only=True)
    destino_descripcion = serializers.CharField(
        source="descripcion_destino", read_only=True
    )
    total_destinatarios = serializers.SerializerMethodField()
    total_acusados = serializers.SerializerMethodField()

    class Meta:
        model = Comunicado
        fields = [
            "id",
            "emisor",
            "emisor_nombre",
            "titulo",
            "cuerpo",
            "tipo_destino",
            "alumno",
            "seccion",
            "destino_descripcion",
            "requiere_acuse",
            "creado_en",
            "total_destinatarios",
            "total_acusados",
        ]
        read_only_fields = ["emisor", "creado_en"]

    def validate(self, attrs):
        # Sirve para create y update: cae al valor de la instancia cuando el
        # campo no viene en el payload. La regla vive en el modelo (fuente unica).
        def actual(campo):
            return attrs.get(campo, getattr(self.instance, campo, None))

        errores = Comunicado.errores_coherencia(
            actual("tipo_destino"),
            alumno=actual("alumno"),
            seccion=actual("seccion"),
        )
        if errores:
            raise serializers.ValidationError(errores)
        return attrs

    def get_total_destinatarios(self, obj):
        return obj.entregas.count()

    def get_total_acusados(self, obj):
        return obj.entregas.filter(acusado_en__isnull=False).count()


class EntregaComunicadoSerializer(serializers.ModelSerializer):
    comunicado_titulo = serializers.CharField(source="comunicado.titulo", read_only=True)
    comunicado_cuerpo = serializers.CharField(source="comunicado.cuerpo", read_only=True)
    requiere_acuse = serializers.BooleanField(
        source="comunicado.requiere_acuse", read_only=True
    )
    alumno_nombre = serializers.StringRelatedField(source="alumno", read_only=True)
    acusado = serializers.BooleanField(read_only=True)

    class Meta:
        model = EntregaComunicado
        fields = [
            "id",
            "comunicado",
            "comunicado_titulo",
            "comunicado_cuerpo",
            "requiere_acuse",
            "alumno",
            "alumno_nombre",
            "entregado_en",
            "acusado_en",
            "acusado",
        ]
        read_only_fields = ["id", "comunicado", "alumno", "entregado_en", "acusado_en"]
