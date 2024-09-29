# books/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('get-dates/', DirectionDates.as_view(), name='get_dates'),
    path('get-tickets/', GetTicket.as_view(), name='get_tickets'),
    path('direction-places/', DirectionPlaces.as_view(), name='direction_places'),
    path('create-ticket/', CreateTicket.as_view(), name='create_ticket'),
    path('directions/', DirectionListView.as_view(), name='direction_list'),
    path('retrieve-paid-ticket/', RetrievePaidTicket.as_view(), name='retrieve_paid_ticket'),
    path('get-ticket/<int:ticket_id>/', GetTicketByIdView.as_view(), name='get_ticket_by_id'),

]
