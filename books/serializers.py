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

class TicketDirectionSerializer(serializers.ModelSerializer):
    from_point = serializers.SerializerMethodField()
    from_bus_station = serializers.SerializerMethodField()
    from_date = serializers.SerializerMethodField()
    from_time = serializers.SerializerMethodField()
    to_point = serializers.SerializerMethodField()
    to_bus_station = serializers.SerializerMethodField()
    to_date = serializers.SerializerMethodField()
    to_time = serializers.SerializerMethodField()
    bus = BusFacilitiesSerializer()
    price = serializers.SerializerMethodField()
    free_places_count = serializers.SerializerMethodField()
    taxi_park = serializers.SerializerMethodField()  # Add as a method field

    class Meta:
        model = Trip
        fields = [
            'id', 'from_point', 'from_bus_station', 'from_date', 'from_time',
            'to_point', 'to_bus_station', 'to_date', 'to_time', 'price',
            'free_places_count', 'bus', 'taxi_park'  # Include the taxi_park field here
        ]

    def get_from_point(self, obj):
        return {"id": obj.route.start_city.id, "name": obj.route.start_city.name}

    def get_to_point(self, obj):
        return {"id": obj.route.end_city.id, "name": obj.route.end_city.name}

    def get_from_bus_station(self, obj):
        first_stop = obj.route.stops.first()
        return {
            "id": first_stop.id if first_stop else None,
            "name": first_stop.name if first_stop else None
        }

    def get_to_bus_station(self, obj):
        last_stop = obj.route.stops.last()
        return {
            "id": last_stop.id if last_stop else None,
            "name": last_stop.name if last_stop else None
        }

    def get_from_date(self, obj):
        return obj.start_date.strftime('%Y-%m-%d')

    def get_from_time(self, obj):
        return obj.departure_time.strftime('%H:%M')

    def get_to_date(self, obj):
        return obj.end_date.strftime('%Y-%m-%d')

    def get_to_time(self, obj):
        return obj.departure_time.strftime('%H:%M')  # Adjust as needed

    def get_price(self, obj):
        return str(obj.ticket_price)

    def get_free_places_count(self, obj):
        # Get all tickets associated with the current trip
        tickets = Ticket.objects.filter(direction=obj)

        # Count all passengers associated with these tickets
        occupied_seats = TicketPassenger.objects.filter(ticket__in=tickets).count()

        # Calculate the number of free seats
        total_seats = obj.bus.count_of_seats
        free_places = total_seats - occupied_seats

        return free_places

    def get_taxi_park(self, obj):
        return "Таксопарк “ТОО ЖОЛЫМБЕТ ПЕРЕВОЗКИ”"



class PassengerTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketPassenger
        fields = ["passenger", "place_num", "place_floor"]


class TicketSerializer(serializers.Serializer):
    direction = serializers.IntegerField()  # This will now be the Trip ID
    place_num = serializers.IntegerField(required=False)
    place_floor = serializers.IntegerField(required=False)
    tickets = PassengerTicketSerializer(many=True, required=False)

    def create(self, validated_data):
        try:
            with transaction.atomic():
                # Fetch the Trip instance using the direction (Trip) ID
                trip = Trip.objects.get(id=validated_data["direction"])
                place_num = validated_data.get("place_num")
                place_floor = validated_data.get("place_floor")
                tickets_data = validated_data.get("tickets", [])

                ticket = Ticket()
                ticket.direction = trip  # Correctly link the ticket to the Trip instance
                ticket.user = self.context["request"].user if self.context["request"].user.is_authenticated else None
                ticket.status = "Booked"
                ticket.save()

                reserved_places = []

                if place_num and place_floor:
                    if TicketPassenger.objects.filter(ticket=ticket, place_num=place_num, place_floor=place_floor).exists():
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

                        if TicketPassenger.objects.filter(ticket=ticket, place_num=place_num, place_floor=place_floor).exists():
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
        fields = ["direction", "place_num", "place_floor", "tickets"]



class TicketDetailSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()
    direction = serializers.SerializerMethodField()
    passengers = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'qr_code', 'direction', 'passengers']

    def get_qr_code(self, obj):
        return f"http://example.com/qr/{obj.id}"

    def get_passengers(self, obj):
        passengers = TicketPassenger.objects.filter(ticket=obj)
        return [{'place_num': p.place_num, 'place_floor': p.place_floor, 'passenger': p.passenger.full_name} for p in passengers]

    def get_direction(self, obj):
        from trip.serializers import TripSerializer  # Import here to avoid circular import
        return TripSerializer(obj.direction).data

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['name', 'travel_time_from_start', 'stop_time']