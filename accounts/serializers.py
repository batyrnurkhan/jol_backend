import logging
from rest_framework import serializers
from .models import CustomUser, Passenger
from books.models import Ticket, TicketPassenger

# Initialize logger for accounts app
logger = logging.getLogger('accounts')

class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class VerificationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=4)

    def validate(self, data):
        logger.debug(f'Validating verification code for phone number: {data.get("phone_number")}')
        return data

class SetPasswordSerializer(serializers.Serializer):
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        logger.debug('Validating passwords')
        if data['password1'] != data['password2']:
            logger.error('Passwords do not match')
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
        logger.debug(f'Validating login data for: {data.get("username") or data.get("phone_number")}')
        if not data.get('username') and not data.get('phone_number'):
            logger.error('Username or phone number is required')
            raise serializers.ValidationError("Username or phone number is required.")
        return data

class UserProfileBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone_number']

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['id', 'full_name', 'document_type', 'document_number_or_iin', 'birth_date']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        validated_data['user'] = user
        logger.debug(f'Creating passenger for user: {user}')
        return super().create(validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'document_type', 'document_number_or_iin', 'birth_date', 'email']
        read_only_fields = ['phone_number']

    def update(self, instance, validated_data):
        # Update the CustomUser profile data
        instance = super().update(instance, validated_data)

        passenger_data = {
            'full_name': validated_data.get('full_name', instance.full_name),
            'document_type': validated_data.get('document_type', instance.document_type),
            'document_number_or_iin': validated_data.get('document_number_or_iin', instance.document_number_or_iin),
            'birth_date': validated_data.get('birth_date', instance.birth_date),
        }

        # Update or create the Passenger associated with the user profile (where is_profile_passenger=True)
        Passenger.objects.update_or_create(
            user=instance,
            is_profile_passenger=True,  # Ensure only the passenger connected to the user profile is updated
            defaults=passenger_data
        )

        return instance

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
        point = {
            "id": obj.direction.route.start_city.id,
            "name": obj.direction.route.start_city.name
        }
        logger.debug(f'Getting from_point for ticket {obj.id}: {point}')
        return point

    def get_to_point(self, obj):
        point = {
            "id": obj.direction.route.end_city.id,
            "name": obj.direction.route.end_city.name
        }
        logger.debug(f'Getting to_point for ticket {obj.id}: {point}')
        return point

    def get_from_date(self, obj):
        date = obj.direction.start_date.strftime('%Y-%m-%d')
        logger.debug(f'Getting from_date for ticket {obj.id}: {date}')
        return date

    def get_to_date(self, obj):
        date = obj.direction.end_date.strftime('%Y-%m-%d')
        logger.debug(f'Getting to_date for ticket {obj.id}: {date}')
        return date

    def get_from_time(self, obj):
        time = obj.direction.departure_time.strftime('%H:%M')
        logger.debug(f'Getting from_time for ticket {obj.id}: {time}')
        return time

    def get_to_time(self, obj):
        time = obj.direction.departure_time.strftime('%H:%M')
        logger.debug(f'Getting to_time for ticket {obj.id}: {time}')
        return time

    def get_bus(self, obj):
        bus_info = {
            "have_toilet": obj.direction.bus.have_toilet,
            "have_wifi": obj.direction.bus.have_wifi,
            "is_recumbent": obj.direction.bus.is_recumbent
        }
        logger.debug(f'Getting bus info for ticket {obj.id}: {bus_info}')
        return bus_info

    def get_free_places_count(self, obj):
        tickets = Ticket.objects.filter(direction=obj.direction)
        occupied_seats = TicketPassenger.objects.filter(ticket__in=tickets).count()
        total_seats = obj.direction.bus.count_of_seats
        free_places = total_seats - occupied_seats
        logger.debug(f'Calculating free places for ticket {obj.id}: {free_places}')
        return free_places
