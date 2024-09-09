import logging
from rest_framework import viewsets
from .models import Bus, Driver
from .serializers import BusListSerializer, BusCreateSerializer, DriverListSerializer, DriverCreateUpdateSerializer

# Initialize logger for buses app
logger = logging.getLogger('buses')

class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            logger.debug(f"Using BusListSerializer for action: {self.action}")
            return BusListSerializer
        logger.debug(f"Using BusCreateSerializer for action: {self.action}")
        return BusCreateSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating a new bus with data: {request.data}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating bus with data: {request.data}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        bus_id = self.get_object().id
        logger.info(f"Deleting bus with ID: {bus_id}")
        return super().destroy(request, *args, **kwargs)

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            logger.debug(f"Using DriverListSerializer for action: {self.action}")
            return DriverListSerializer
        logger.debug(f"Using DriverCreateUpdateSerializer for action: {self.action}")
        return DriverCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating a new driver with data: {request.data}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating driver with data: {request.data}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        driver_id = self.get_object().id
        logger.info(f"Deleting driver with ID: {driver_id}")
        return super().destroy(request, *args, **kwargs)
