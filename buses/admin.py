from django.contrib import admin
from .models import Bus, Stamp, Model, Driver, Seat

# Register your models here.

admin.site.register(Bus)
admin.site.register(Stamp)
admin.site.register(Model)
admin.site.register(Driver)
admin.site.register(Seat)