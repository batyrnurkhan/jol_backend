from django.contrib import admin
from .models import Route, Stop, City

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('start_city', 'end_city', 'total_travel_time', 'created_at')
    search_fields = ('start_city', 'end_city')

@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ('route', 'name', 'travel_time_from_start', 'stop_time')
    search_fields = ('name',)

admin.site.register(City)