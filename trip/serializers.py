from rest_framework import serializers
from .models import Trip
from datetime import date

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'

    def get_status(self, obj):
        today = date.today()

        if not obj.active:
            return "Flight cancelled" if obj.end_date < today else "The flight is not on sale"

        if obj.start_date <= today <= obj.end_date:
            return "The flight is active, sales are underway"

        if today < obj.start_date:
            return f"Flight scheduled from {obj.start_date} to {obj.end_date}"

        return "Flight completed"