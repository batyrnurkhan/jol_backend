# accounts/views.py
import logging
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import PhoneNumberSerializer, VerificationCodeSerializer, CompleteProfileSerializer
from .utils import send_sms
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
