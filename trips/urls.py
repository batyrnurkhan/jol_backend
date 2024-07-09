from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PointViewSet, BusStationViewSet, DirectionViewSet

router = DefaultRouter()
router.register(r'points', PointViewSet)
router.register(r'bus-stations', BusStationViewSet)
router.register(r'directions', DirectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
