import random
import string
from django.db import models


def generate_bus_id():
    return ''.join(random.choices(string.digits, k=6))


class Bus(models.Model):
    id = models.CharField(max_length=6, primary_key=True, default=generate_bus_id, editable=False, unique=True)
    count_of_seats = models.PositiveIntegerField()
    have_toilet = models.BooleanField(default=False)
    have_wifi = models.BooleanField(default=False)
    is_recumbent = models.BooleanField(default=False)
    floors = models.PositiveIntegerField(choices=[(1, 'One'), (2, 'Two')], default=1)

    def __str__(self):
        return f"Bus {self.id}"
