# accounts/views.py
import logging
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import DestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Passenger
from .serializers import PhoneNumberSerializer, VerificationCodeSerializer, CompleteProfileSerializer, LoginSerializer, \
    UserProfileSerializer, PassengerSerializer, UserProfileBasicSerializer
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token

import random

logger = logging.getLogger(__name__)

CustomUser = get_user_model()
FIXED_VERIFICATION_CODE = "1234"  # This is the fixed verification code


class PhoneNumberView(APIView):
    def post(self, request):
        logger.info("Received data: %s", request.data)
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            # Imitate sending SMS by directly using the fixed verification code
            cache.set(phone_number, FIXED_VERIFICATION_CODE, timeout=300)  # Store code in cache for 5 minutes
            return Response({"message": "Verification code set"}, status=status.HTTP_200_OK)
        logger.error("Invalid data: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']
            stored_code = cache.get(phone_number)
            if stored_code and stored_code == code:
                user, created = CustomUser.objects.get_or_create(phone_number=phone_number)
                return Response({"message": "Phone number verified", "user_id": user.id}, status=status.HTTP_200_OK)
            return Response({"message": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteProfileView(APIView):
    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompleteProfileSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            user = authenticate(request, phone_number=phone_number, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileBasicView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileBasicSerializer(request.user)
        return Response(serializer.data)


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdatePersonalInfoView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PassengerInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        passengers = Passenger.objects.filter(user=request.user)
        serializer = PassengerSerializer(passengers, many=True)
        return Response(serializer.data)


class IndividualPassengerView(generics.RetrieveAPIView):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class DeletePassengerView(DestroyAPIView):
    queryset = Passenger.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SecurityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        security_info = {
            'data_protection_policy': 'Your data is protected...',
            'last_security_update': '2024-07-01'
        }
        return Response(security_info)


class FAQView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        faq_info = [
            {'question': 'How to change my password?', 'answer': 'Go to settings...'},
            {'question': 'How to delete my account?', 'answer': 'Contact support...'}
        ]
        return Response(faq_info)


class SupportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        support_info = {
            'support_email': 'support@example.com',
            'support_phone': '+1234567890'
        }
        return Response(support_info)


class CreatePassenger(APIView):
    def post(self, request):
        serializer = PassengerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response("OK", status=status.HTTP_201_CREATED)
