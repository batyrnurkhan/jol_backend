import logging
from django.core.exceptions import ValidationError
from django.db import models
from accounts.models import CustomUser, Passenger
from trip.models import Trip

# Initialize logger for books app
logger = logging.getLogger('books')

class Ticket(models.Model):
    TICKET_STATUSES = [
        ("Booked", "Booked"),
        ("Payed", "Payed"),
        ("Expired", "Expired"),
    ]

    direction = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="tickets")
    status = models.CharField(max_length=8, choices=TICKET_STATUSES, default="Booked")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        logger.debug(f"Saving ticket with status: {self.status} for user: {self.user}")
        super().save(*args, **kwargs)

class TicketPassenger(models.Model):
    ticket = models.ForeignKey(Ticket, related_name="passenger_tickets", on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # Field for storing user if ticket was bought for them
    place_num = models.IntegerField()
    place_floor = models.IntegerField()

    def save(self, *args, **kwargs):
        logger.debug(
            f"Attempting to save TicketPassenger: Ticket {self.ticket.id}, Passenger {self.passenger}, User {self.user}, Place {self.place_num}, Floor {self.place_floor}")

        # Fetch TicketPassengers for the same trip only
        tps = TicketPassenger.objects.filter(ticket__direction=self.ticket.direction, ticket=self.ticket)

        for tp in tps:
            if tp.place_num == self.place_num and tp.place_floor == self.place_floor:
                logger.error(
                    f"ValidationError: This place {self.place_num} on {self.place_floor} floor is already taken by {tp.passenger.full_name if tp.passenger else 'another user'}")
                raise ValidationError(
                    f"This place {self.place_num} on {self.place_floor} floor is already taken by {tp.passenger.full_name if tp.passenger else 'another user'}")

        super().save(*args, **kwargs)

    def clean(self):
        logger.debug(f"Cleaning data for TicketPassenger: Ticket {self.ticket.id}, Passenger {self.passenger}, User {self.user}, Place {self.place_num}, Floor {self.place_floor}")
        tps = TicketPassenger.objects.filter(ticket__direction=self.ticket.direction)
        for tp in tps:
            if self.passenger and tp.passenger == self.passenger:
                logger.error(f"ValidationError during clean: This passenger {self.passenger.full_name} already has place {tp.place_num}, {tp.place_floor} floor")
                raise ValidationError(f"This passenger {self.passenger.full_name} already has place {tp.place_num}, {tp.place_floor} floor")
            if self.user and tp.user == self.user:
                logger.error(f"ValidationError during clean: This user already has place {tp.place_num}, {tp.place_floor} floor")
                raise ValidationError(f"This user already has place {tp.place_num}, {tp.place_floor} floor")
            if tp.place_num == self.place_num and tp.place_floor == self.place_floor:
                logger.error(f"ValidationError during clean: This place {self.place_num} on {self.place_floor} floor is already taken by {tp.passenger.full_name if tp.passenger else 'another user'}")
                raise ValidationError(f"This place {self.place_num} on {self.place_floor} floor is already taken by {tp.passenger.full_name if tp.passenger else 'another user'}")

    class Meta:
        unique_together = ['ticket', 'place_num', 'place_floor']
        logger.debug(f"Meta: Unique together constraint on ['ticket', 'place_num', 'place_floor']")
