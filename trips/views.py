from rest_framework import viewsets
from .models import Point, BusStation, Direction
from .serializers import PointSerializer, BusStationSerializer, DirectionSerializer

class PointViewSet(viewsets.ModelViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer

class BusStationViewSet(viewsets.ModelViewSet):
    queryset = BusStation.objects.all()
    serializer_class = BusStationSerializer

class DirectionViewSet(viewsets.ModelViewSet):
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer
