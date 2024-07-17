from rest_framework import serializers
from .models import Point, BusStation, Direction

class PointNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['id', 'name']

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['id', 'name', 'region']

class BusStationNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusStation
        fields = ['id', 'name']

class BusStationSerializer(serializers.ModelSerializer):
    point = PointSerializer()  # Nested serializer to display point details

    class Meta:
        model = BusStation
        fields = ['id', 'name', 'point']

class DirectionSerializer(serializers.ModelSerializer):
    from_point = PointSerializer()
    to_point = PointSerializer()
    from_bus_station = BusStationSerializer()
    to_bus_station = BusStationSerializer()

    class Meta:
        model = Direction
        fields = ['id', 'from_point', 'to_point', 'from_bus_station', 'to_bus_station', 'from_datetime', 'to_datetime', 'bus', 'price']
