from django.core.exceptions import ValidationError
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
    status = models.CharField(max_length=8, choices=TICKET_STATUSES, default="Booked")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)


class TicketPassenger(models.Model):
    ticket = models.ForeignKey(Ticket, related_name="passenger_tickets", on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    place_num = models.IntegerField()
    place_floor = models.IntegerField()

    def clean(self):
        tps = TicketPassenger.objects.filter(ticket__direction=self.ticket.direction)
        for tp in tps:
            if tp.place_num == self.place_num and tp.place_floor == self.place_floor:
                raise ValidationError(f"This place is already taken")

