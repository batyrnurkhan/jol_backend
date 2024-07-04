from django.contrib import admin
from trips.models import Point, BusStation, Direction

admin.site.register(Point)
admin.site.register(BusStation)
admin.site.register(Direction)