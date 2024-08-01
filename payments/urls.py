from django.urls import path
from .views import *

urlpatterns = [
    path('pay-ticket/', PayTicket.as_view(), name='pay_ticket'),
]
