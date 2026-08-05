"""
Vistas de la app `comunicados` (fase 1).

`ComunicadoViewSet`: CRUD para el emisor (admin/autoridad/docente). Al crear,
sella el `emisor` con el token y dispara el fan-out on write dentro de una
transacción (o queda el comunicado CON sus entregas, o no queda nada).

El scoping por alcance del emisor (destino ⊆ alcance) y la categoría llegan en
fase 2: acá la emisión está acotada solo por ROL (permissions.py). La bandeja del
familiar y el acuse (RF09/RF10) llegan en HU-08 (`MiBandejaViewSet`).
"""

from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Comunicado
from .permissions import EmiteAdminAutoridadODocente
from .serializers import ComunicadoSerializer, EntregaComunicadoSerializer


class ComunicadoViewSet(viewsets.ModelViewSet):
    queryset = Comunicado.objects.select_related("emisor", "seccion", "alumno").all()
    serializer_class = ComunicadoSerializer
    permission_classes = [EmiteAdminAutoridadODocente]

    def perform_create(self, serializer):
        # Atomico: o queda el comunicado CON sus entregas, o no queda nada. Sin
        # esto, si generar_entregas() falla, quedaria un broadcast huerfano
        # (persistido pero sin destinatarios).
        with transaction.atomic():
            comunicado = serializer.save(emisor=self.request.user)
            comunicado.generar_entregas()

    @action(detail=True, methods=["get"], url_path="entregas")
    def entregas(self, request, pk=None):
        """Estado de acuse del comunicado, entrega por entrega."""
        comunicado = self.get_object()
        qs = comunicado.entregas.select_related("familiar", "alumno")
        return Response(EntregaComunicadoSerializer(qs, many=True).data)
