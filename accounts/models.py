# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    full_name = models.CharField(_('ФИО'), max_length=255, blank=True, null=True)
    document_type = models.CharField(_('тип документа'), max_length=50, blank=True, null=True)
    document_number_or_iin = models.CharField(_('номер документа или ИИН'), max_length=100, unique=True, blank=True,
                                              null=True)
    birth_date = models.DateField(_('дата рождения'), blank=True, null=True)
    email = models.EmailField(_('электронная почта'), unique=True, blank=True, null=True)
    phone_number = models.CharField(_('номер телефона'), max_length=15, unique=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number


class Passenger(models.Model):
    user = models.ForeignKey(CustomUser, related_name='passengers', on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(_('ФИО пассажира'), max_length=255)
    document_type = models.CharField(_('тип документа'), max_length=50)
    document_number_or_iin = models.CharField(_('номер документа или ИИН'), max_length=100)
    birth_date = models.DateField(_('дата рождения'))

    def __str__(self):
        return self.full_name
