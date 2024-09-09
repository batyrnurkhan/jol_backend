import logging
from rest_framework import viewsets
from .models import City, Stop, Route
from .serializers import CitySerializer, StopSerializer, RouteSerializer

logger = logging.getLogger('trip_v2')

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def list(self, request, *args, **kwargs):
        logger.info("Listing all cities")
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating a new city with data: {request.data}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        city_id = self.get_object().id
        logger.info(f"Updating City ID {city_id} with data: {request.data}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        city_id = self.get_object().id
        logger.info(f"Deleting City ID {city_id}")
        return super().destroy(request, *args, **kwargs)

class StopViewSet(viewsets.ModelViewSet):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer

    def list(self, request, *args, **kwargs):
        logger.info("Listing all stops")
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating a new stop with data: {request.data}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        stop_id = self.get_object().id
        logger.info(f"Updating Stop ID {stop_id} with data: {request.data}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        stop_id = self.get_object().id
        logger.info(f"Deleting Stop ID {stop_id}")
        return super().destroy(request, *args, **kwargs)

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def list(self, request, *args, **kwargs):
        logger.info("Listing all routes")
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating a new route with data: {request.data}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        route_id = self.get_object().id
        logger.info(f"Updating Route ID {route_id} with data: {request.data}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        route_id = self.get_object().id
        logger.info(f"Deleting Route ID {route_id}")
        return super().destroy(request, *args, **kwargs)
