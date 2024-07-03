from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusViewSet

router = DefaultRouter()
router.register(r'buses', BusViewSet)

urlpatterns = [
    path('buses/', include(router.urls)),
]
