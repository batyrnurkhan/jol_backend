# accounts/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('send-code/', PhoneNumberView.as_view(), name='send_code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]
