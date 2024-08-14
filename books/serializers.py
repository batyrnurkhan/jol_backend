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
    place_num = serializers.IntegerField(required=False)
    place_floor = serializers.IntegerField(required=False)
    tickets = PassengerTicketSerializer(many=True, required=False)

    def create(self, validated_data):
        try:
            with transaction.atomic():
                direction = Direction.objects.get(id=validated_data["direction"])
                place_num = validated_data.get("place_num")
                place_floor = validated_data.get("place_floor")
                tickets_data = validated_data.get("tickets", [])

                ticket = Ticket()
                ticket.direction = direction
                ticket.user = self.context["request"].user if self.context["request"].user.is_authenticated else None
                ticket.status = "Booked"
                ticket.save()

                reserved_places = []

                if place_num and place_floor:
                    if TicketPassenger.objects.filter(ticket__direction=direction, place_num=place_num, place_floor=place_floor).exists():
                        raise ValidationError(f"Place {place_num} on floor {place_floor} is already taken.")

                    TicketPassenger.objects.create(
                        ticket=ticket,
                        user=self.context["request"].user,  # Сохраняем пользователя, если билет для него
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

                        if TicketPassenger.objects.filter(ticket__direction=direction, place_num=place_num, place_floor=place_floor).exists():
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

                return reserved_places

        except Direction.DoesNotExist:
            raise ValidationError("Direction does not exist")
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(str(e))

    class Meta:
        fields = ["direction", "place_num", "place_floor", "tickets"]


class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = '__all__'

class TicketDetailSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()
    direction = DirectionSerializer()
    passengers = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'qr_code', 'direction', 'passengers']

    def get_qr_code(self, obj):
        # Assuming you have a method to generate QR codes
        return f"http://example.com/qr/{obj.id}"

    def get_passengers(self, obj):
        passengers = TicketPassenger.objects.filter(ticket=obj)
        return [{'place_num': p.place_num, 'place_floor': p.place_floor, 'passenger': p.passenger.full_name} for p in passengers]