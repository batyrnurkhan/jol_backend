from django.contrib import admin
from .models import Trip

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'route', 'bus', 'driver', 'departure_time', 'start_date', 'end_date', 'ticket_price', 'frequency')
    list_filter = ('route', 'bus', 'driver', 'start_date', 'end_date', 'frequency')
    search_fields = ('route__start_city', 'route__end_city', 'bus__name', 'driver__full_name')
