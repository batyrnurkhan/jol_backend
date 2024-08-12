from rest_framework import viewsets
from .models import Bus, Driver
from .serializers import BusListSerializer, BusCreateSerializer, DriverListSerializer, DriverCreateUpdateSerializer


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return BusListSerializer
        return BusCreateSerializer


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return DriverListSerializer
        return DriverCreateUpdateSerializer