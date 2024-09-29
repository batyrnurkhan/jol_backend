import logging
from django.core.exceptions import ValidationError
from django.db import models
from accounts.models import CustomUser, Passenger
from trip.models import Trip

# Initialize logger for books app
logger = logging.getLogger('books')
from django.utils import timezone
from datetime import timedelta

class Ticket(models.Model):
    TICKET_STATUSES = [
        ("Booked", "Booked"),
        ("Payed", "Payed"),
        ("Expired", "Expired"),
    ]

    direction = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="tickets")
    status = models.CharField(max_length=8, choices=TICKET_STATUSES, default="Booked")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    booked_at = models.DateTimeField(null=True, blank=True)  # Add booked timestamp

    def save(self, *args, **kwargs):
        if self.status == "Booked" and self.booked_at is None:
            self.booked_at = timezone.now()
        super().save(*args, **kwargs)

    def is_locked(self):
        """Check if the ticket is locked for booking (within 30 minutes)."""
        if self.status == "Booked" and self.booked_at:
            elapsed_time = timezone.now() - self.booked_at
            return elapsed_time < timedelta(minutes=30)
        return False

    def check_and_expire(self):
        """Automatically expire the ticket if 30 minutes have passed since booking."""
        if self.status == "Booked" and self.booked_at:
            elapsed_time = timezone.now() - self.booked_at
            if elapsed_time >= timedelta(minutes=30):
                self.status = "Expired"
                self.save()

class TicketPassenger(models.Model):
    ticket = models.ForeignKey(Ticket, related_name="passenger_tickets", on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # Field for storing user if ticket was bought for them
    place_num = models.IntegerField()
    place_floor = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        logger.debug(
            f"Attempting to save TicketPassenger: Ticket {self.ticket.id}, Passenger {self.passenger}, User {self.user}, Place {self.place_num}, Floor {self.place_floor}")
        # Filter TicketPassengers by the exact same trip
        tps = TicketPassenger.objects.filter(ticket=self.ticket)

        for tp in tps:
            # Check if the exact place on the same floor is already taken
            if tp.place_num == self.place_num and tp.place_floor == self.place_floor:
                logger.error(f"ValidationError: Place {self.place_num} on floor {self.place_floor} is already taken.")
                raise ValidationError(
                    f"Place {self.place_num} on floor {self.place_floor} is already taken by {tp.passenger.full_name if tp.passenger else 'another user'}")

        super().save(*args, **kwargs)

    def clean(self):
        logger.debug(
            f"Cleaning data for TicketPassenger: Ticket {self.ticket.id}, Place {self.place_num}, Floor {self.place_floor}")
        tps = TicketPassenger.objects.filter(ticket=self.ticket)

        for tp in tps:
            # Same as in save, but for cleaning before saving
            if tp.place_num == self.place_num and tp.place_floor == self.place_floor:
                logger.error(
                    f"ValidationError during clean: Place {self.place_num} on {self.place_floor} floor is already taken.")
                raise ValidationError(
                    f"This place {self.place_num} on {self.place_floor} floor is already taken by {tp.passenger.full_name if tp.passenger else 'another user'}")
    class Meta:
        unique_together = ['ticket', 'place_num', 'place_floor']
        logger.debug(f"Meta: Unique together constraint on ['ticket', 'place_num', 'place_floor']")
