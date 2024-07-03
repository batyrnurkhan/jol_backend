# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('full_name', 'document_type', 'document_number_or_iin', 'birth_date', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'is_staff', 'is_superuser')}
         ),
    )
    list_display = ('phone_number', 'email', 'full_name', 'is_staff', 'is_active')
    search_fields = ('phone_number', 'email', 'full_name')
    ordering = ('phone_number',)


admin.site.register(CustomUser, CustomUserAdmin)
