import logging
import datetime
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from trip_v2.models import Route, Stop
from books.models import Ticket, TicketPassenger
from buses.models import Bus, Seat
from trip.models import Trip

# Initialize logger for books app
logger = logging.getLogger('books')


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
    taxi_park = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'from_point', 'from_bus_station', 'from_date', 'from_time',
            'to_point', 'to_bus_station', 'to_date', 'to_time', 'price',
            'free_places_count', 'bus', 'taxi_park'
        ]

    def get_from_point(self, obj):
        point = {"id": obj.route.start_city.id, "name": obj.route.start_city.name}
        logger.debug(f"Getting from_point: {point}")
        return point

    def get_to_point(self, obj):
        point = {"id": obj.route.end_city.id, "name": obj.route.end_city.name}
        logger.debug(f"Getting to_point: {point}")
        return point

    def get_from_bus_station(self, obj):
        first_stop = obj.route.stops.first()
        bus_station = {
            "id": first_stop.id if first_stop else None,
            "name": first_stop.name if first_stop else None
        }
        logger.debug(f"Getting from_bus_station: {bus_station}")
        return bus_station

    def get_to_bus_station(self, obj):
        last_stop = obj.route.stops.last()
        bus_station = {
            "id": last_stop.id if last_stop else None,
            "name": last_stop.name if last_stop else None
        }
        logger.debug(f"Getting to_bus_station: {bus_station}")
        return bus_station

    def get_from_date(self, obj):
        date = obj.start_date.strftime('%Y-%m-%d')
        logger.debug(f"Getting from_date: {date}")
        return date

    def get_from_time(self, obj):
        time = obj.departure_time.strftime('%H:%M')
        logger.debug(f"Getting from_time: {time}")
        return time

    def get_to_date(self, obj):
        date = obj.end_date.strftime('%Y-%m-%d')
        logger.debug(f"Getting to_date: {date}")
        return date

    def get_to_time(self, obj):
        time = obj.departure_time.strftime('%H:%M')
        logger.debug(f"Getting to_time: {time}")
        return time

    def get_price(self, obj):
        price = str(obj.ticket_price)
        logger.debug(f"Getting price: {price}")
        return price

    def get_free_places_count(self, obj):
        tickets = Ticket.objects.filter(direction=obj)
        occupied_seats = TicketPassenger.objects.filter(ticket__in=tickets).count()
        total_seats = obj.bus.count_of_seats
        free_places = total_seats - occupied_seats
        logger.debug(f"Calculating free_places_count: {free_places}")
        return free_places

    def get_taxi_park(self, obj):
        taxi_park = "Таксопарк “ТОО ЖОЛЫМБЕТ ПЕРЕВОЗКИ”"
        logger.debug(f"Getting taxi_park: {taxi_park}")
        return taxi_park


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
                trip = Trip.objects.get(id=validated_data["direction"])
                logger.debug(f"Creating ticket for trip ID: {trip.id}")

                place_num = validated_data.get("place_num")
                place_floor = validated_data.get("place_floor")
                tickets_data = validated_data.get("tickets", [])

                ticket = Ticket()
                ticket.direction = trip
                ticket.user = self.context["request"].user if self.context["request"].user.is_authenticated else None
                ticket.status = "Booked"
                ticket.save()
                logger.info(f"Ticket created with ID: {ticket.id} for user: {ticket.user}")

                reserved_places = []

                if place_num and place_floor:
                    # Validate seat type
                    seat = Seat.objects.filter(seat_id=place_num, bus=trip.bus).first()  # Corrected query
                    if seat is None:
                        raise ValidationError(f"Seat {place_num} does not exist on this bus.")
                    if seat.seat_type in ["aisle", "driver"]:
                        raise ValidationError(f"Seat {seat.seat_id} cannot be booked as it is for {seat.seat_type}.")

                    if TicketPassenger.objects.filter(ticket=ticket, place_num=place_num,
                                                      place_floor=place_floor).exists():
                        logger.error(f"ValidationError: Place {place_num} on floor {place_floor} is already taken.")
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
                    logger.info(f"Place reserved: {place_num}, Floor: {place_floor} for ticket ID: {ticket.id}")

                elif tickets_data:
                    for ticket_data in tickets_data:
                        passenger = ticket_data.get("passenger")
                        place_num = ticket_data["place_num"]
                        place_floor = ticket_data["place_floor"]

                        # Validate seat type
                        seat = Seat.objects.filter(seat_id=place_num, bus=trip.bus).first()  # Corrected query
                        if seat is None:
                            raise ValidationError(f"Seat {place_num} does not exist on this bus.")
                        if seat.seat_type in ["aisle", "driver"]:
                            raise ValidationError(
                                f"Seat {seat.seat_id} cannot be booked as it is for {seat.seat_type}.")

                        if TicketPassenger.objects.filter(ticket=ticket, place_num=place_num,
                                                          place_floor=place_floor).exists():
                            logger.error(f"ValidationError: Place {place_num} on floor {place_floor} is already taken.")
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
                        logger.info(
                            f"Passenger place reserved: {place_num}, Floor: {place_floor} for ticket ID: {ticket.id}")

                else:
                    logger.error("ValidationError: Either place_num and place_floor or tickets must be provided.")
                    raise ValidationError("Either place_num and place_floor or tickets must be provided.")

                return ticket, reserved_places

        except Trip.DoesNotExist:
            logger.error("ValidationError: Trip does not exist")
            raise ValidationError("Trip does not exist")
        except ValidationError as e:
            logger.error(f"ValidationError during ticket creation: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Exception during ticket creation: {str(e)}")
            raise ValidationError(str(e))

    class Meta:
        fields = ["direction", "place_num", "place_floor", "tickets"]


class TicketDetailSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()
    direction = serializers.SerializerMethodField()
    passengers = serializers.SerializerMethodField()
    status = serializers.CharField()  # Include status

    class Meta:
        model = Ticket
        fields = ['id', 'qr_code', 'direction', 'passengers', 'status']  # Add 'status' to fields

    def get_qr_code(self, obj):
        qr_code_url = f"http://example.com/qr/{obj.id}"
        logger.debug(f"Getting QR code URL: {qr_code_url}")
        return qr_code_url

    def get_passengers(self, obj):
        passengers = TicketPassenger.objects.filter(ticket=obj)
        passenger_list = [{
            'place_num': p.place_num,
            'place_floor': p.place_floor,
            'passenger': p.passenger.full_name if p.passenger else "Unknown Passenger"
        } for p in passengers]
        logger.debug(f"Getting passengers for ticket ID: {obj.id} - {passenger_list}")
        return passenger_list

    def get_direction(self, obj):
        from trip.serializers import TripSerializer
        direction_data = TripSerializer(obj.direction).data
        logger.debug(f"Getting direction for ticket ID: {obj.id} - {direction_data}")
        return direction_data


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['name', 'travel_time_from_start', 'stop_time']
