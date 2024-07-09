from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Point, BusStation, Direction
from .serializers import PointSerializer, BusStationSerializer, DirectionSerializer

class PointViewSet(viewsets.ModelViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer

    @action(detail=False, methods=['get'])
    def by_region(self, request, *args, **kwargs):
        region = request.query_params.get('region')
        if region:
            points = Point.objects.filter(region=region)
            serializer = self.get_serializer(points, many=True)
            return Response(serializer.data)
        return Response({"error": "Region not provided"}, status=status.HTTP_400_BAD_REQUEST)

class BusStationViewSet(viewsets.ModelViewSet):
    queryset = BusStation.objects.all()
    serializer_class = BusStationSerializer

    @action(detail=False, methods=['get'])
    def by_point(self, request, *args, **kwargs):
        point_id = request.query_params.get('point_id')
        if point_id:
            bus_stations = BusStation.objects.filter(point_id=point_id)
            serializer = self.get_serializer(bus_stations, many=True)
            return Response(serializer.data)
        return Response({"error": "Point ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

class DirectionViewSet(viewsets.ModelViewSet):
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer

    @action(detail=False, methods=['get'])
    def by_bus(self, request, *args, **kwargs):
        bus_id = request.query_params.get('bus_id')
        if bus_id:
            directions = Direction.objects.filter(bus_id=bus_id)
            serializer = self.get_serializer(directions, many=True)
            return Response(serializer.data)
        return Response({"error": "Bus ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
