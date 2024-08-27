from rest_framework import serializers

from books.serializers import BusFacilitiesSerializer
from .models import Trip
from datetime import date

class TripSerializer(serializers.ModelSerializer):
    from_city = serializers.CharField(source='route.start_city')
    to_city = serializers.CharField(source='route.end_city')
    route = serializers.SerializerMethodField()
    bus = BusFacilitiesSerializer()

    class Meta:
        model = Trip
        fields = [
            'id', 'departure_time', 'start_date', 'end_date', 'ticket_price',
            'frequency', 'weekdays', 'status', 'route', 'bus', 'driver',
            'from_city', 'to_city'  # Include the city names in the output
        ]

    def get_route(self, obj):
        return {
            "start_city": obj.route.start_city.name,  # Use .name to get the city name
            "end_city": obj.route.end_city.name,  # Use .name to get the city name
            "total_travel_time": obj.route.total_travel_time
        }

    def get_status(self, obj):
        today = date.today()

        if not obj.active:
            return "Flight cancelled" if obj.end_date < today else "The flight is not on sale"

        if obj.start_date <= today <= obj.end_date:
            return "The flight is active, sales are underway"

        if today < obj.start_date:
            return f"Flight scheduled from {obj.start_date} to {obj.end_date}"

        return "Flight completed"