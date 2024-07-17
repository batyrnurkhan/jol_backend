from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from buses.models import Bus

class Point(models.Model):
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BusStation(models.Model):
    name = models.CharField(max_length=255)
    point = models.ForeignKey(Point, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Direction(models.Model):
    from_point = models.ForeignKey(Point, related_name='departures', on_delete=models.CASCADE)
    to_point = models.ForeignKey(Point, related_name='arrivals', on_delete=models.CASCADE)
    from_bus_station = models.ForeignKey(BusStation, related_name='departures', on_delete=models.SET_NULL, null=True, blank=True)
    to_bus_station = models.ForeignKey(BusStation, related_name='arrivals', on_delete=models.SET_NULL, null=True, blank=True)
    from_datetime = models.DateTimeField()
    to_datetime = models.DateTimeField()
    bus = models.ForeignKey(Bus, related_name='directions', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def free_places_count(self):
        tickets = self.tickets.filter(Q(status="Payed") | Q(status="Booked"))
        return self.bus.count_of_seats - tickets.count()

    def travel_time(self):
        return self.to_datetime - self.from_datetime

    def __str__(self):
        return f"{self.from_point} to {self.to_point} by {self.bus}"

    def clean(self):
        overlapping_directions = Direction.objects.filter(
            bus=self.bus,
            from_datetime__lt=self.to_datetime,
            to_datetime__gt=self.from_datetime
        ).exclude(id=self.id)

        if overlapping_directions.exists():
            raise ValidationError(f"The bus {self.bus} is already assigned to another direction during the specified period.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
