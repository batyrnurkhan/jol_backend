import logging
from django.db import models
from trip_v2.models import Route
from buses.models import Bus, Driver
from datetime import datetime

# Initialize logger for trip app
logger = logging.getLogger('trip')

class Trip(models.Model):
    STATUS_CHOICES = [
        ('active', 'Рейс активен, идут продажи'),
        ('not_on_sale', 'Рейс не в продаже'),
        ('cancelled', 'Рейс отменен'),
        ('scheduled', 'с {start_date} по {end_date}'),
    ]

    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips')
    departure_time = models.TimeField()
    start_date = models.DateField()
    end_date = models.DateField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=255)  # e.g., 'Daily', 'Several times a week'
    weekdays = models.JSONField()  # {"Monday": True, "Tuesday": False, ...}
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self):
        trip_info = (f"Trip from {self.route.start_city} to {self.route.end_city} "
                     f"with {self.bus.name} driven by {self.driver.full_name}")
        logger.debug(f"String representation of Trip called: {trip_info}")
        return trip_info

    @property
    def come_to_point(self):
        """Calculate the arrival time based on the departure time and total travel time."""
        if self.departure_time and self.route.total_travel_time:
            # Convert departure_time to a datetime object for easier calculation
            departure_datetime = datetime.combine(self.start_date, self.departure_time)
            arrival_datetime = departure_datetime + self.route.total_travel_time
            return arrival_datetime.time()  # Return only the time part
        return None

    def save(self, *args, **kwargs):
        logger.info(f"Saving Trip: Route {self.route}, Bus {self.bus}, Driver {self.driver}")
        super().save(*args, **kwargs)

