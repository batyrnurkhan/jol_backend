# accounts/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('send-code/', PhoneNumberView.as_view(), name='send_code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('complete-profile/<int:user_id>/', CompleteProfileView.as_view(), name='complete_profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileBasicView.as_view(), name='profile'),
    path('profile/personal-info/', UserProfileView.as_view(), name='personal_info'),
    path('profile/personal-info/update/', UpdatePersonalInfoView.as_view(), name='update_personal_info'),
    path('profile/passenger-info/', PassengerInfoView.as_view(), name='passenger_info'),
    path('profile/passenger-info/<int:pk>/', IndividualPassengerView.as_view(),
         name='individual_passenger_info'),
    path('profile/passenger-info/<int:pk>/delete/', DeletePassengerView.as_view(), name='delete_passenger'),
    path('profile/security/', SecurityView.as_view(), name='security'),
    path('profile/faq/', FAQView.as_view(), name='faq'),
    path('profile/support/', SupportView.as_view(), name='support'),
]
