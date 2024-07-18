import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import Passenger
from books.models import Ticket, TicketPassenger
from buses.models import Bus
from trips.models import Direction
from trips.serializers import BusStationNameSerializer, PointNameSerializer


class BusFacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['have_toilet', 'have_wifi', 'is_recumbent']


class TicketDirectionSerializer(serializers.ModelSerializer):
    free_places_count = serializers.SerializerMethodField()
    from_point = PointNameSerializer()
    from_bus_station = BusStationNameSerializer()
    to_point = PointNameSerializer()
    to_bus_station = BusStationNameSerializer()
    from_date = serializers.SerializerMethodField()
    from_time = serializers.SerializerMethodField()
    to_date = serializers.SerializerMethodField()
    to_time = serializers.SerializerMethodField()
    bus = BusFacilitiesSerializer()

    class Meta:
        model = Direction
        fields = ['id', 'from_point', 'from_bus_station', 'from_date', 'from_time',
                  'to_point', 'to_bus_station', 'to_date', 'to_time',
                  'price', 'free_places_count', 'bus']

    def get_free_places_count(self, obj):
        return obj.free_places_count()

    def get_from_date(self, obj):
        return obj.from_datetime.date().strftime('%Y-%m-%d')

    def get_from_time(self, obj):
        return obj.from_datetime.time().strftime('%H:%M')

    def get_to_date(self, obj):
        return obj.to_datetime.date().strftime('%Y-%m-%d')

    def get_to_time(self, obj):
        return obj.to_datetime.time().strftime('%H:%M')


class PassengerTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketPassenger
        fields = ["passenger", "place_num", "place_floor"]


class TicketSerializer(serializers.Serializer):
    direction = serializers.IntegerField()
    passengers = PassengerTicketSerializer(many=True)

    def create(self, validated_data):
        try:
            with transaction.atomic():
                direction = Direction.objects.get(id=validated_data["direction"])
                passengers_data = validated_data["passengers"]

                ticket = Ticket()
                ticket.direction = direction
                ticket.user = self.context["request"].user if self.context["request"].user.is_authenticated else None
                ticket.status = "Booked"
                ticket.save()

                for pass_data in passengers_data:
                    passenger = pass_data["passenger"]
                    if not passenger:
                        raise ValidationError("No existing passenger")
                    passenger_ticket = TicketPassenger()
                    passenger_ticket.ticket = ticket
                    passenger_ticket.passenger = passenger
                    passenger_ticket.place_num = pass_data["place_num"]
                    passenger_ticket.place_floor = pass_data["place_floor"]
                    passenger_ticket.save()
                    print("created")
        except Direction.DoesNotExist:
            raise ValidationError("Direction does not exist")
        except Passenger.DoesNotExist:
            raise ValidationError("Passenger does not exist")
        except ValidationError as e:
            # Optionally, you can add custom logging or handling here
            raise e
        except Exception as e:
            # Catch any other exceptions
            raise ValidationError(str(e))

    class Meta:
        fields = ["direction", "passengers"]
