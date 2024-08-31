from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, StopViewSet, RouteViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'stops', StopViewSet)
router.register(r'routes', RouteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
