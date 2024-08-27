from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RouteViewSet, CityListView

router = DefaultRouter()
router.register(r'routes', RouteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cities/', CityListView.as_view(), name='city_list'),  # Add this line
]
