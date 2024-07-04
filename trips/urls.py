from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PointViewSet, BusStationViewSet, DirectionViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = DefaultRouter()
router.register(r'points', PointViewSet)
router.register(r'bus-stations', BusStationViewSet)
router.register(r'directions', DirectionViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Bus API",
        default_version='v1',
        description="API documentation for the Bus app",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@bus.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
