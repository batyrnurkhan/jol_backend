# books/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('get_dates/', DirectionDates.as_view(), name='get_dates'),
]
