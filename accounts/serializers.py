# accounts/serializers.py
from rest_framework import serializers
from .models import CustomUser, Passenger


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class VerificationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=4)

class SetPasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match")
        return data

class CompleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'document_type', 'document_number_or_iin', 'birth_date', 'email']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    phone_number = serializers.CharField(max_length=15, required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        if not data.get('username') and not data.get('phone_number'):
            raise serializers.ValidationError("Username or phone number is required.")
        return data


# accounts/serializers.py
from rest_framework import serializers
from .models import CustomUser, Passenger


class UserProfileBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone_number']


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['id', 'full_name', 'document_type', 'document_number_or_iin', 'birth_date']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'full_name', 'document_type', 'document_number_or_iin', 'birth_date', 'email']
        read_only_fields = ['phone_number']

from rest_framework import serializers
from books.models import Ticket, TicketPassenger

class MyTicketPassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketPassenger
        fields = ['place_num', 'place_floor']

class MyTicketSerializer(serializers.ModelSerializer):
    from_point = serializers.SerializerMethodField()
    from_date = serializers.SerializerMethodField()
    from_time = serializers.SerializerMethodField()
    to_point = serializers.SerializerMethodField()
    to_date = serializers.SerializerMethodField()
    to_time = serializers.SerializerMethodField()
    bus = serializers.SerializerMethodField()
    free_places_count = serializers.SerializerMethodField()
    price = serializers.DecimalField(source='direction.ticket_price', max_digits=10, decimal_places=2)
    status = serializers.CharField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'from_point', 'from_date', 'from_time', 'to_point',
            'to_date', 'to_time', 'price', 'free_places_count', 'bus', 'status'
        ]

    def get_from_point(self, obj):
        return {
            "id": obj.direction.route.start_city.id,
            "name": obj.direction.route.start_city.name
        }

    def get_to_point(self, obj):
        return {
            "id": obj.direction.route.end_city.id,
            "name": obj.direction.route.end_city.name
        }

    def get_from_date(self, obj):
        return obj.direction.start_date.strftime('%Y-%m-%d')

    def get_to_date(self, obj):
        return obj.direction.end_date.strftime('%Y-%m-%d')

    def get_from_time(self, obj):
        return obj.direction.departure_time.strftime('%H:%M')

    def get_to_time(self, obj):
        return obj.direction.departure_time.strftime('%H:%M')

    def get_bus(self, obj):
        return {
            "have_toilet": obj.direction.bus.have_toilet,
            "have_wifi": obj.direction.bus.have_wifi,
            "is_recumbent": obj.direction.bus.is_recumbent
        }

    def get_free_places_count(self, obj):
        # Get all tickets associated with the current trip
        tickets = Ticket.objects.filter(direction=obj.direction)

        # Count all passengers associated with these tickets
        occupied_seats = TicketPassenger.objects.filter(ticket__in=tickets).count()

        # Calculate the number of free seats
        total_seats = obj.direction.bus.count_of_seats
        free_places = total_seats - occupied_seats

        return free_places

