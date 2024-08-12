from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusViewSet, DriverViewSet

router = DefaultRouter()
router.register(r'buses', BusViewSet)
router.register(r'drivers', DriverViewSet)  # Register the DriverViewSet

urlpatterns = [
    path('', include(router.urls)),
]
