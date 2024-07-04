# accounts/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('accounts/send-code/', PhoneNumberView.as_view(), name='send_code'),
    path('accounts/verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('accounts/complete-profile/<int:user_id>/', CompleteProfileView.as_view(), name='complete_profile'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/profile/', UserProfileView.as_view(), name='profile'),
    path('accounts/profile/personal-info/', PersonalInfoView.as_view(), name='personal_info'),
    path('accounts/profile/passenger-info/', PassengerInfoView.as_view(), name='passenger_info'),
    path('accounts/profile/passenger-info/<int:pk>/', IndividualPassengerView.as_view(),
         name='individual_passenger_info'),
    path('accounts/profile/security/', SecurityView.as_view(), name='security'),
    path('accounts/profile/faq/', FAQView.as_view(), name='faq'),
    path('accounts/profile/support/', SupportView.as_view(), name='support'),
]
