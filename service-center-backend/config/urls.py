from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    ClientViewSet,
    ServiceViewSet,
    OrderViewSet,
    OrderServiceViewSet
)

router = DefaultRouter()

router.register(r'clients', ClientViewSet, basename='clients')
router.register(r'services', ServiceViewSet, basename='services')
router.register(r'orders', OrderViewSet, basename='orders')

router.register(
    r'order-services',
    OrderServiceViewSet,
    basename='order-services'
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]