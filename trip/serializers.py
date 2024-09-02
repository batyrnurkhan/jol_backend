import logging
from rest_framework import serializers
from buses.serializers import BusDetailSerializer, DriverListSerializer
from trip_v2.serializers import RouteSerializer
from .models import Trip, Bus, Route
from datetime import date

# Initialize logger for trip app
logger = logging.getLogger('trip')


class TripSerializer(serializers.ModelSerializer):
    from_city = serializers.CharField(source='route.start_city.name', read_only=True)
    to_city = serializers.CharField(source='route.end_city.name', read_only=True)
    route = RouteSerializer(read_only=True)  # Use the detailed RouteSerializer
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

    def get_status_description(self, obj):
        today = date.today()

        if obj.status == 'cancelled':
            description = "Flight cancelled"
        elif obj.status == 'not_on_sale':
            description = "The flight is not on sale"
        elif obj.status == 'active' and obj.start_date <= today <= obj.end_date:
            description = "The flight is active, sales are underway"
        elif obj.status == 'scheduled':
            description = f"Flight scheduled from {obj.start_date} to {obj.end_date}"
        elif today > obj.end_date:
            description = "Flight completed"
        else:
            description = "Unknown status"

        logger.debug(f"Status description for Trip ID {obj.id}: {description}")
        return description

    def create(self, validated_data):
        bus_data = validated_data.pop('bus')
        route_data = validated_data.pop('route')  # Assuming route data is provided and needs to be handled similarly

        logger.info(f"Creating Bus with data: {bus_data}")
        bus = Bus.objects.create(**bus_data)

        logger.info(f"Creating Route with data: {route_data}")
        route = Route.objects.create(**route_data)  # This assumes you need to create the Route instance here

        trip = Trip.objects.create(bus=bus, route=route, **validated_data)
        logger.info(f"Trip created with ID: {trip.id}, Route: {route}, Bus: {bus}")
        return trip
