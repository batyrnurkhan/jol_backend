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
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)


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
    direction_name = serializers.CharField(source='direction.name')
    from_date = serializers.SerializerMethodField()
    to_date = serializers.SerializerMethodField()
    from_time = serializers.SerializerMethodField()
    to_time = serializers.SerializerMethodField()
    price = serializers.IntegerField(source='direction.price')
    passengers = MyTicketPassengerSerializer(source='passenger_tickets', many=True)

    class Meta:
        model = Ticket
        fields = ['direction_name', 'from_date', 'to_date', 'from_time', 'to_time', 'price', 'passengers']

    def get_from_date(self, obj):
        return obj.direction.from_datetime.date().strftime('%d %b')

    def get_to_date(self, obj):
        return obj.direction.to_datetime.date().strftime('%d %b')

    def get_from_time(self, obj):
        return obj.direction.from_datetime.time().strftime('%H:%M')

    def get_to_time(self, obj):
        return obj.direction.to_datetime.time().strftime('%H:%M')