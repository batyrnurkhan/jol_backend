from rest_framework import serializers
from buses.serializers import BusDetailSerializer, DriverListSerializer
from .models import Trip, Bus, Route
from datetime import date


class TripSerializer(serializers.ModelSerializer):
    from_city = serializers.CharField(source='route.start_city.name', read_only=True)
    to_city = serializers.CharField(source='route.end_city.name', read_only=True)
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all())
    bus = BusDetailSerializer()  # Use the detailed serializer here
    driver = DriverListSerializer()  # Include driver details here
    status_description = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'departure_time', 'start_date', 'end_date', 'ticket_price',
            'frequency', 'weekdays', 'status', 'route', 'bus', 'driver',
            'from_city', 'to_city', 'status_description'
        ]

    def get_route(self, obj):
        return {
            "start_city": obj.route.start_city.name,
            "end_city": obj.route.end_city.name,
            "total_travel_time": obj.route.total_travel_time
        }

    def get_status_description(self, obj):
        today = date.today()

        if obj.status == 'cancelled':
            return "Flight cancelled"
        elif obj.status == 'not_on_sale':
            return "The flight is not on sale"
        elif obj.status == 'active' and obj.start_date <= today <= obj.end_date:
            return "The flight is active, sales are underway"
        elif obj.status == 'scheduled':
            return f"Flight scheduled from {obj.start_date} to {obj.end_date}"
        elif today > obj.end_date:
            return "Flight completed"
        else:
            return "Unknown status"

    def create(self, validated_data):
        bus_data = validated_data.pop('bus')
        bus = Bus.objects.create(**bus_data)

        route = validated_data.pop('route')  # Get the route object

        trip = Trip.objects.create(bus=bus, route=route, **validated_data)
        return trip
