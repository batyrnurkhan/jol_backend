import logging
from rest_framework import serializers
from .models import Bus, Driver, Seat

# Initialize logger for buses app
logger = logging.getLogger('buses')

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['seat_id', 'seat_col', 'seat_row', 'seat_type']


class BusCreateSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True)

    class Meta:
        model = Bus
        fields = [
            'name', 'stamp', 'model', 'state_number', 'VIN',
            'count_of_seats', 'have_toilet', 'have_wifi',
            'is_recumbent', 'scheme', 'floors', 'seats'
        ]

    def create(self, validated_data):
        seats_data = validated_data.pop('seats')
        bus = Bus.objects.create(**validated_data)
        for seat_data in seats_data:
            Seat.objects.create(bus=bus, **seat_data)
        return bus

class BusListSerializer(serializers.ModelSerializer):
    model_stamp = serializers.SerializerMethodField()

    class Meta:
        model = Bus
        fields = ['id', 'model_stamp', 'state_number', 'count_of_seats']

    def get_model_stamp(self, obj):
        model_stamp = f"{obj.stamp.name} {obj.model.name}" if obj.stamp and obj.model else ""
        logger.debug(f"Getting model_stamp for Bus ID {obj.id}: {model_stamp}")
        return model_stamp

class DriverCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['picture', 'full_name', 'date_of_birth', 'license_number', 'license_issue_date']

    def create(self, validated_data):
        logger.info(f"Creating Driver with data: {validated_data}")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        logger.info(f"Updating Driver ID {instance.id} with data: {validated_data}")
        return super().update(instance, validated_data)

class DriverListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'full_name', 'date_of_birth', 'picture']

class BusDetailSerializer(serializers.ModelSerializer):
    model_stamp = serializers.SerializerMethodField()

    class Meta:
        model = Bus
        fields = [
            'id', 'name', 'model_stamp', 'state_number', 'VIN',
            'count_of_seats', 'have_toilet', 'have_wifi',
            'is_recumbent', 'scheme', 'floors'
        ]

    def get_model_stamp(self, obj):
        model_stamp = f"{obj.stamp.name} {obj.model.name}" if obj.stamp and obj.model else ""
        logger.debug(f"Getting model_stamp for Bus ID {obj.id}: {model_stamp}")
        return model_stamp

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['seat_id', 'seat_col', 'seat_row', 'seat_type']