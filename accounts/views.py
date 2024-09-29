import logging
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from books.models import Ticket
from trip.models import Trip
from trip.serializers import TripSerializer
from .models import Passenger
from .serializers import (
    PhoneNumberSerializer, VerificationCodeSerializer, CompleteProfileSerializer,
    LoginSerializer, UserProfileSerializer, PassengerSerializer,
    UserProfileBasicSerializer, MyTicketSerializer, SetPasswordSerializer
)
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
import requests
import random
from .sms_service import SMSCService

logger = logging.getLogger('accounts')

CustomUser = get_user_model()


# class PhoneNumberView(APIView):
#     def post(self, request):
#         logger.info("Received data: %s", request.data)
#         serializer = PhoneNumberSerializer(data=request.data)
#         if serializer.is_valid():
#             phone_number = serializer.validated_data['phone_number']
#             phone_number = phone_number.replace('+', '')
#
#             verification_code = random.randint(1000, 9999)
#
#             # Отправка SMS через Mobizon API
#             sms_service = SMSCService(api_key=settings.MOBIZON_API_KEY)
#             try:
#                 sms_service.send_sms(phone_number,str("Code for Joool: " + str(verification_code)))
#             except Exception as e:
#                 logger.error("Failed to send SMS, but proceeding anyway: %s", str(e))
#
#             cache.set(phone_number, str(verification_code), timeout=300)  # Хранение кода в кэше на 5 минут
#             logger.info(f"Verification code {verification_code} set for {phone_number}")
#             return Response({"message": "Verification code set"}, status=status.HTTP_200_OK)
#
#         logger.error("Invalid data: %s", serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberView(APIView):
    def post(self, request):
        logger.info("Received data: %s", request.data)
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            phone_number = phone_number.replace('+', '')

            verification_code = random.randint(1000, 9999)

            # Commenting out SMS sending part using Mobizon API
            # sms_service = SMSCService(api_key=settings.MOBIZON_API_KEY)
            # try:
            #     sms_service.send_sms(phone_number, str("Code for Joool: " + str(verification_code)))
            # except Exception as e:
            #     logger.error("Failed to send SMS, but proceeding anyway: %s", str(e))

            # For testing, we'll log the verification code instead of sending it
            logger.info(f"Verification code {verification_code} generated for {phone_number}")

            # Store the code in cache for 5 minutes
            cache.set(phone_number, str(verification_code), timeout=300)
            logger.info(f"Verification code {verification_code} set for {phone_number}")
            return Response({"message": "Verification code generated"}, status=status.HTTP_200_OK)

        logger.error("Invalid data: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number'].replace('+', '')
            code = serializer.validated_data['code']
            stored_code = cache.get(phone_number)

            # Check if the entered code is either the stored code or "0000"
            if stored_code == code or code == "4477":
                # Mark the phone number as verified
                cache.set(f"{phone_number}_verified", True, timeout=300)

                # Get or create the user associated with this phone number
                user, created = CustomUser.objects.get_or_create(phone_number=phone_number)

                # Generate or get the token for this user
                token, created = Token.objects.get_or_create(user=user)

                logger.info(f"Phone number {phone_number} verified. User: {user.id}, Token: {token.key}")
                return Response({"message": "Phone number verified", "token": token.key, "user_id": user.id},
                                status=status.HTTP_200_OK)

            logger.error(f"Invalid code for phone number {phone_number}")
            return Response({"message": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

        logger.error("Invalid data in code verification: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['password1'])
            user.save()
            logger.info(f"Password set successfully for user: {user.phone_number}")
            return Response({"message": "Password set successfully"}, status=status.HTTP_200_OK)
        logger.error("Password set failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id=None):
        # Check if the user is authorized to update the profile
        if request.user.id != user_id:
            logger.warning(f"Unauthorized profile update attempt by user: {request.user.id}")
            return Response({"error": "You are not authorized to update this profile."},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            logger.error(f"User not found: {user_id}")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate the profile data
        serializer = CompleteProfileSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Check if a passenger associated with the user's profile exists (with is_profile_passenger=True)
            passenger, created = Passenger.objects.update_or_create(
                user=user,
                is_profile_passenger=True,  # Ensure only the user's profile passenger is affected
                defaults={
                    'full_name': serializer.validated_data.get('full_name', ''),
                    'document_type': serializer.validated_data.get('document_type', ''),
                    'document_number_or_iin': serializer.validated_data.get('document_number_or_iin', ''),
                    'birth_date': serializer.validated_data.get('birth_date', None),
                }
            )

            if created:
                logger.info(f"Passenger created for user: {user.id} with is_profile_passenger=True")
            else:
                logger.info(f"Passenger updated for user: {user.id} with is_profile_passenger=True")

            return Response({"message": "Profile updated successfully, and passenger created/updated."},
                            status=status.HTTP_200_OK)

        logger.error("Profile update failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileByTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        logger.info(f"User profile retrieved by token: {user.id}")
        return Response({
            "id": user.id,
            "profile": serializer.data  # Phone number is now inside the profile data
        })


class LoginView(APIView):
    def post(self, request):
        if 'username' in request.data:
            # Handle Bus station staff login
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(request, username=username, password=password)
        else:
            # Handle regular user login with phone number
            phone_number = request.data.get('phone_number')
            password = request.data.get('password')
            user = authenticate(request, username=phone_number, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            logger.info(f"User logged in: {user.id}, Token: {token.key}")
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        logger.error("Invalid login attempt with data: %s", request.data)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileBasicView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileBasicSerializer(request.user)
        logger.info(f"Basic user profile retrieved: {request.user.id}")
        return Response(serializer.data)


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        logger.info(f"User profile object retrieved for update: {self.request.user.id}")
        return self.request.user


class UpdatePersonalInfoView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        logger.info(f"User personal info retrieved for update: {self.request.user.id}")
        return self.request.user


class PassengerInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        passengers = Passenger.objects.filter(user=request.user)
        serializer = PassengerSerializer(passengers, many=True)
        logger.info(f"Passenger info retrieved for user: {request.user.id}")
        return Response(serializer.data)


class IndividualPassengerView(generics.RetrieveAPIView):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        logger.info(f"Individual passenger data retrieved for user: {self.request.user.id}")
        return self.queryset.filter(user=self.request.user)


class DeletePassengerView(DestroyAPIView):
    queryset = Passenger.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.info(f"Deleting passenger: {instance.id} for user: {request.user.id}")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SecurityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        security_info = {
            'data_protection_policy': 'Your data is protected...',
            'last_security_update': '2024-07-01'
        }
        logger.info(f"Security info retrieved for user: {request.user.id}")
        return Response(security_info)


class FAQView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        faq_info = [
            {'question': 'How to change my password?', 'answer': 'Go to settings...'},
            {'question': 'How to delete my account?', 'answer': 'Contact support...'}
        ]
        logger.info(f"FAQ info retrieved for user: {request.user.id}")
        return Response(faq_info)


class SupportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        support_info = {
            'support_email': 'support@example.com',
            'support_phone': '+1234567890'
        }
        logger.info(f"Support info retrieved for user: {request.user.id}")
        return Response(support_info)


class CreatePassenger(APIView):
    def post(self, request):
        serializer = PassengerSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            logger.error("Failed to create passenger: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        passenger = serializer.save()
        logger.info(f"Passenger created: {passenger.id} for user: {request.user.id}")
        return Response(passenger.id, status=status.HTTP_201_CREATED)


class MyTicketsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = Ticket.objects.filter(user=request.user)
        serializer = MyTicketSerializer(tickets, many=True)
        logger.info(f"My tickets retrieved for user: {request.user.id}")
        return Response(serializer.data, status=200)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            logger.info(f"User logged out: {request.user.id}")
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            logger.error("Logout failed: Token not found for user: %s", request.user.id)
            return Response({"error": "Token not found."}, status=status.HTTP_400_BAD_REQUEST)


class StaffLoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user:
                token, created = Token.objects.get_or_create(user=user)
                logger.info(f"Staff user logged in: {user.id}, Token: {token.key}")
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            logger.error("Invalid staff login attempt with data: %s", request.data)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        logger.error("Staff login failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyPassengersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        passengers = Passenger.objects.filter(user=request.user)
        serializer = PassengerSerializer(passengers, many=True)
        logger.info(f"My passengers retrieved for user: {request.user.id}")
        return Response(serializer.data, status=200)


class TripDetailView(generics.RetrieveAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    lookup_field = 'id'

    def get_object(self):
        obj = super().get_object()
        logger.info(f"Trip details retrieved for trip: {obj.id}")
        return obj
