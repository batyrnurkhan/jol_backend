# accounts/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('accounts/send-code/', PhoneNumberView.as_view(), name='send_code'),
    path('accounts/verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('accounts/register/', UserRegistrationView.as_view(), name='register'),
    path('accounts/login/', LoginView.as_view(), name='login'),
]
