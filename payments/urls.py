from django.urls import path
from .views import *

urlpatterns = [
    path('pay-ticket/', PayTicket.as_view(), name='pay_ticket'),
    path('refund-ticket/', RefundTicket.as_view(), name='refund-ticket'),
]
