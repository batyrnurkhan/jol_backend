from django.db import models


class City(models.Model):
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}, {self.region}"

class Route(models.Model):
    start_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='start_routes')
    end_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='end_routes')
    total_travel_time = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.start_city.name} -> {self.end_city.name}"

class Stop(models.Model):
    route = models.ForeignKey(Route, related_name='stops', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    travel_time_from_start = models.DurationField()
    stop_time = models.DurationField()

    def __str__(self):
        return f"Stop at {self.name} on {self.route}"
