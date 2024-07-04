from django.apps import apps
from django.db import models
from django.db.models import Q

from buses.models import Bus  # Correctly importing the Bus model


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
    from_bus_station = models.ForeignKey(BusStation, related_name='departures', on_delete=models.CASCADE)
    to_bus_station = models.ForeignKey(BusStation, related_name='arrivals', on_delete=models.CASCADE)
    from_datetime = models.DateTimeField()
    to_datetime = models.DateTimeField()
    bus = models.ForeignKey(Bus, related_name='directions', on_delete=models.CASCADE)  # Adding related_name
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def is_free(self):
        tickets = self.tickets.filter(Q(status="Payed") | Q(status="Booked"))
        count = self.bus.count_of_seats - tickets.count()
        return count > 0

    def __str__(self):
        return f"{self.from_point} to {self.to_point} by {self.bus}"
