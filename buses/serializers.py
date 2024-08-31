from rest_framework import serializers
from .models import Bus, Driver


class BusCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = [
            'name', 'stamp', 'model', 'state_number', 'VIN',
            'count_of_seats', 'have_toilet', 'have_wifi',
            'is_recumbent', 'scheme', 'floors'
        ]

class BusListSerializer(serializers.ModelSerializer):
    model_stamp = serializers.SerializerMethodField()

    class Meta:
        model = Bus
        fields = ['id', 'model_stamp', 'state_number', 'count_of_seats']

    def get_model_stamp(self, obj):
        return f"{obj.stamp.name} {obj.model.name}" if obj.stamp and obj.model else ""


class DriverCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['picture', 'full_name', 'date_of_birth', 'license_number', 'license_issue_date']

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
        return f"{obj.stamp.name} {obj.model.name}" if obj.stamp and obj.model else ""
