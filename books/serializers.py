import datetime

from rest_framework import serializers

from books.models import Ticket
from buses.models import Bus
from trips.models import Direction
from trips.serializers import BusStationNameSerializer, PointNameSerializer


class BusFacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['have_toilet', 'have_wifi', 'is_recumbent']


class TicketDirectionSerializer(serializers.ModelSerializer):
    free_places_count = serializers.SerializerMethodField()
    from_point = PointNameSerializer()
    from_bus_station = BusStationNameSerializer()
    to_point = PointNameSerializer()
    to_bus_station = BusStationNameSerializer()
    from_date = serializers.SerializerMethodField()
    from_time = serializers.SerializerMethodField()
    to_date = serializers.SerializerMethodField()
    to_time = serializers.SerializerMethodField()
    bus = BusFacilitiesSerializer()

    class Meta:
        model = Direction
        fields = ['id', 'from_point', 'from_bus_station', 'from_date', 'from_time',
                  'to_point', 'to_bus_station', 'to_date', 'to_time',
                  'price', 'free_places_count', 'bus']

    def get_free_places_count(self, obj):
        return obj.free_places_count()

    def get_from_date(self, obj):
        return obj.from_datetime.date().strftime('%Y-%m-%d')

    def get_from_time(self, obj):
        return obj.from_datetime.time().strftime('%H:%M')

    def get_to_date(self, obj):
        return obj.to_datetime.date().strftime('%Y-%m-%d')

    def get_to_time(self, obj):
        return obj.to_datetime.time().strftime('%H:%M')


class TicketSerializer(serializers.Serializer):
    direction = serializers.IntegerField()
    user = serializers.IntegerField(required=False)
    passenger_ids = serializers.ListSerializer(allow_empty=False)
    phone_number = serializers.CharField(required=False)
    email = serializers.CharField(required=False)

    class Meta:
        fields = ["direction", "user", "passenger_ids", "phone_number", "email"]
