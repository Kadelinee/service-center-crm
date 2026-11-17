from rest_framework import viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Clients, Services, Orders, OrderServices
from .serializers import (
    ClientSerializer,
    ServiceSerializer,
    OrderSerializer,
    OrderServiceSerializer
)

class IsAuthenticatedReadOnlyOrStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Clients.objects.all().order_by('client_id')

    serializer_class = ClientSerializer

    permission_classes = [IsAuthenticatedReadOnlyOrStaff]

class ServiceViewSet(viewsets.ModelViewSet):

    queryset = Services.objects.all().order_by('service_id')

    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all().order_by('order_id')

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]

class OrderServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderServices.objects.select_related(
        'order',
        'service'
    ).all().order_by('order_service_id')

    serializer_class = OrderServiceSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]
