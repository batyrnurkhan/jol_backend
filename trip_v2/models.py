from django.db import models

class Route(models.Model):
    start_city = models.CharField(max_length=255)
    end_city = models.CharField(max_length=255)
    total_travel_time = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.start_city} -> {self.end_city}"

class Stop(models.Model):
    route = models.ForeignKey(Route, related_name='stops', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    travel_time_from_start = models.DurationField()
    stop_time = models.DurationField()

    def __str__(self):
        return f"Stop at {self.name} on {self.route}"
