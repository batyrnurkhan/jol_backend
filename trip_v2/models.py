import logging
from django.db import models

# Initialize logger for trip_v2 app
logger = logging.getLogger('trip_v2')

class City(models.Model):
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255)

    def __str__(self):
        city_info = f"{self.name}, {self.region}"
        logger.debug(f"String representation of City called: {city_info}")
        return city_info

class Route(models.Model):
    start_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='start_routes')
    end_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='end_routes')
    total_travel_time = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        route_info = f"{self.start_city.name} -> {self.end_city.name}"
        logger.debug(f"String representation of Route called: {route_info}")
        return route_info

class Stop(models.Model):
    route = models.ForeignKey(Route, related_name='stops', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    travel_time_from_start = models.DurationField()
    stop_time = models.DurationField()

    def __str__(self):
        stop_info = f"Stop at {self.name} on {self.route}"
        logger.debug(f"String representation of Stop called: {stop_info}")
        return stop_info
