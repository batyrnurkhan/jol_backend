import logging
import random
import string
from django.db import models

# Initialize logger for buses app
logger = logging.getLogger('buses')

def generate_bus_id():
    bus_id = ''.join(random.choices(string.digits, k=6))
    logger.debug(f"Generated bus ID: {bus_id}")
    return bus_id

def bus_scheme_upload_to(instance, filename):
    path = f"bus_schemes/{instance.id}/{filename}"
    logger.debug(f"Uploading bus scheme to: {path}")
    return path

class Stamp(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        logger.debug(f"String representation of Stamp called: {self.name}")
        return self.name

class Model(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        logger.debug(f"String representation of Model called: {self.name}")
        return f"{self.name}"

class Bus(models.Model):
    id = models.CharField(max_length=6, primary_key=True, default=generate_bus_id, editable=False, unique=True)
    name = models.CharField(max_length=255)
    stamp = models.ForeignKey('Stamp', on_delete=models.SET_NULL, null=True, related_name='buses')
    model = models.ForeignKey('Model', on_delete=models.SET_NULL, null=True, related_name='buses')
    state_number = models.CharField(max_length=10)  # Format XXX AAA XX
    VIN = models.CharField(max_length=17)
    count_of_seats = models.PositiveIntegerField()
    have_toilet = models.BooleanField(default=False)
    have_wifi = models.BooleanField(default=False)
    is_recumbent = models.BooleanField(default=False)
    scheme = models.FileField(upload_to=bus_scheme_upload_to, null=True, blank=True)
    floors = models.PositiveIntegerField(choices=[(1, 'One'), (2, 'Two')], default=1)
    def __str__(self):
        bus_info = f"Bus {self.name} ({self.id})"
        logger.debug(f"String representation of Bus called: {bus_info}")
        return bus_info

def driver_picture_upload_to(instance, filename):
    path = f"drivers/{instance.id}/{filename}"
    logger.debug(f"Uploading driver picture to: {path}")
    return path

class Driver(models.Model):
    picture = models.ImageField(upload_to=driver_picture_upload_to, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    license_number = models.CharField(max_length=20, unique=True)
    license_issue_date = models.DateField()

    def __str__(self):
        logger.debug(f"String representation of Driver called: {self.full_name}")
        return self.full_name
