# accounts/admin.py
from django.contrib import admin
from .models import CustomUser, Passenger


class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 1


class CustomUserAdmin(admin.ModelAdmin):
    inlines = [PassengerInline]
    list_display = ('phone_number', 'full_name', 'email', 'is_staff', 'is_active')
    search_fields = ('phone_number', 'full_name', 'email')
    ordering = ('phone_number',)


class PassengerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'document_type', 'document_number_or_iin', 'birth_date')
    search_fields = ('full_name', 'document_number_or_iin', 'user__phone_number')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Passenger, PassengerAdmin)
