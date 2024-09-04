import logging
from rest_framework import serializers

from buses.models import Driver
from buses.serializers import BusDetailSerializer, DriverListSerializer
from trip_v2.serializers import RouteSerializer
from .models import Trip, Bus, Route
from datetime import date

# Initialize logger for trip app
logger = logging.getLogger('trip')


class TripSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all())
    bus = serializers.PrimaryKeyRelatedField(queryset=Bus.objects.all())
    driver = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all())
    weekdays = serializers.ListField(child=serializers.CharField(), allow_empty=False)  # List of weekdays
    frequency = serializers.CharField(max_length=255)  # Frequency as a string

    class Meta:
        model = Trip
        fields = [
            'id', 'departure_time', 'start_date', 'end_date', 'ticket_price',
            'frequency', 'weekdays', 'status', 'route', 'bus', 'driver'
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
        route = validated_data.pop('route')
        bus = validated_data.pop('bus')
        driver = validated_data.pop('driver')

        # Create the Trip instance
        trip = Trip.objects.create(route=route, bus=bus, driver=driver, **validated_data)
        return trip
