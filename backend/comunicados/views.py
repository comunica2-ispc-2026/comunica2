"""
Vistas de la app `comunicados` (fase 1).

- `ComunicadoViewSet`: CRUD para el emisor (admin/autoridad/docente). Al crear,
  sella el `emisor` con el token y dispara el fan-out on write dentro de una
  transacción. El scoping por alcance/categoría llega en fase 2.
- `MiBandejaViewSet`: la bandeja del familiar, de solo lectura. Filtra por el
  token (`request.user`), NUNCA por un id de la URL — mismo principio de "lo mío"
  que `MisAlumnosViewSet`. El acuse (RF09/RF10) es la acción `acusar/`.
"""

from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Comunicado, EntregaComunicado
from .permissions import EmiteAdminAutoridadODocente
from .serializers import ComunicadoSerializer, EntregaComunicadoSerializer


class ComunicadoViewSet(viewsets.ModelViewSet):
    queryset = Comunicado.objects.select_related("emisor", "seccion", "alumno").all()
    serializer_class = ComunicadoSerializer
    permission_classes = [EmiteAdminAutoridadODocente]

    def perform_create(self, serializer):
        # Atomico: o queda el comunicado CON sus entregas, o no queda nada.
        with transaction.atomic():
            comunicado = serializer.save(emisor=self.request.user)
            comunicado.generar_entregas()

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
