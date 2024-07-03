from django.db import models
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
    from_bus_station = models.ForeignKey(BusStation, related_name='departures', on_delete=models.CASCADE)
    to_bus_station = models.ForeignKey(BusStation, related_name='arrivals', on_delete=models.CASCADE)
    from_datetime = models.DateTimeField()
    to_datetime = models.DateTimeField()
    bus = models.ForeignKey('buses.Bus', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.from_point} to {self.to_point} by {self.bus}"
