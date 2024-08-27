import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from trip_v2.models import Route, Stop
from books.models import Ticket, TicketPassenger
from buses.models import Bus
from trip.models import Trip


class BusFacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['have_toilet', 'have_wifi', 'is_recumbent']

class TripSerializer(serializers.ModelSerializer):
    route = serializers.SerializerMethodField()
    bus = BusFacilitiesSerializer()

    class Meta:
        model = Trip
        fields = ['id', 'route', 'departure_time', 'start_date', 'end_date', 'ticket_price', 'bus', 'driver', 'frequency', 'weekdays', 'active']

    def get_route(self, obj):
        return {
            "start_city": obj.route.start_city,
            "end_city": obj.route.end_city,
            "total_travel_time": obj.route.total_travel_time
        }

class TicketDirectionSerializer(serializers.ModelSerializer):
    free_places_count = serializers.SerializerMethodField()
    from_stop = serializers.SerializerMethodField()
    to_stop = serializers.SerializerMethodField()
    from_date = serializers.SerializerMethodField()
    from_time = serializers.SerializerMethodField()
    to_date = serializers.SerializerMethodField()
    to_time = serializers.SerializerMethodField()
    bus = BusFacilitiesSerializer()

    class Meta:
        model = Route
        fields = ['id', 'from_stop', 'from_date', 'from_time',
                  'to_stop', 'to_date', 'to_time',
                  'total_travel_time', 'free_places_count', 'bus']

    def get_free_places_count(self, obj):
        # Assuming you have a method to calculate free places
        return obj.free_places_count()

    def get_from_stop(self, obj):
        return StopSerializer(obj.stops.first()).data

    def get_to_stop(self, obj):
        return StopSerializer(obj.stops.last()).data

    def get_from_date(self, obj):
        return obj.created_at.date().strftime('%Y-%m-%d')

    def get_from_time(self, obj):
        # Adjust this to use the appropriate time field
        return obj.created_at.time().strftime('%H:%M')

    def get_to_date(self, obj):
        # Assuming you have an arrival time field or can calculate it
        return (obj.created_at + obj.total_travel_time).date().strftime('%Y-%m-%d')

    def get_to_time(self, obj):
        # Assuming you have an arrival time field or can calculate it
        return (obj.created_at + obj.total_travel_time).time().strftime('%H:%M')


class PassengerTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketPassenger
        fields = ["passenger", "place_num", "place_floor"]


class TicketSerializer(serializers.Serializer):
    trip = serializers.IntegerField()
    place_num = serializers.IntegerField(required=False)
    place_floor = serializers.IntegerField(required=False)
    tickets = PassengerTicketSerializer(many=True, required=False)

    def create(self, validated_data):
        try:
            with transaction.atomic():
                trip = Trip.objects.get(id=validated_data["trip"])
                place_num = validated_data.get("place_num")
                place_floor = validated_data.get("place_floor")
                tickets_data = validated_data.get("tickets", [])

                ticket = Ticket()
                ticket.direction = trip.route  # Linking the ticket to the trip's route
                ticket.user = self.context["request"].user if self.context["request"].user.is_authenticated else None
                ticket.status = "Booked"
                ticket.save()

                reserved_places = []

                if place_num and place_floor:
                    if TicketPassenger.objects.filter(ticket__direction=trip.route, place_num=place_num, place_floor=place_floor).exists():
                        raise ValidationError(f"Place {place_num} on floor {place_floor} is already taken.")

                    TicketPassenger.objects.create(
                        ticket=ticket,
                        user=self.context["request"].user,
                        place_num=place_num,
                        place_floor=place_floor
                    )
                    reserved_places.append({
                        "place_num": place_num,
                        "place_floor": place_floor
                    })
                elif tickets_data:
                    for ticket_data in tickets_data:
                        passenger = ticket_data.get("passenger")
                        place_num = ticket_data["place_num"]
                        place_floor = ticket_data["place_floor"]

                        if TicketPassenger.objects.filter(ticket__direction=trip.route, place_num=place_num, place_floor=place_floor).exists():
                            raise ValidationError(f"Place {place_num} on floor {place_floor} is already taken.")

                        TicketPassenger.objects.create(
                            ticket=ticket,
                            passenger=passenger,
                            place_num=place_num,
                            place_floor=place_floor
                        )
                        reserved_places.append({
                            "place_num": place_num,
                            "place_floor": place_floor
                        })
                else:
                    raise ValidationError("Either place_num and place_floor or tickets must be provided.")

                return ticket, reserved_places

        except Trip.DoesNotExist:
            raise ValidationError("Trip does not exist")
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(str(e))

    class Meta:
        fields = ["trip", "place_num", "place_floor", "tickets"]

class TicketDetailSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()
    trip = TripSerializer()
    passengers = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'qr_code', 'trip', 'passengers']

    def get_qr_code(self, obj):
        # Assuming you have a method to generate QR codes
        return f"http://example.com/qr/{obj.id}"

    def get_passengers(self, obj):
        passengers = TicketPassenger.objects.filter(ticket=obj)
        return [{'place_num': p.place_num, 'place_floor': p.place_floor, 'passenger': p.passenger.full_name} for p in passengers]
class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['name', 'travel_time_from_start', 'stop_time']