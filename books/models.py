from django.db import models

from accounts.models import CustomUser, Passenger
from trips.models import Direction


# Create your models here.
class Ticket(models.Model):
    TICKET_STATUSES = [
        ("Booked", "Booked"),
        ("Payed", "Payed"),
        ("Expired", "Expired"),
    ]

    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name="tickets")
    status = models.CharField(max_length=8, choices=TICKET_STATUSES)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.SET_NULL, null=True, blank=True)
    place_num = models.IntegerField()
    place_floor = models.IntegerField()
