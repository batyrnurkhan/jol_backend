import datetime
import json

from django.db.models import Min, F, Q
from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Ticket, TicketPassenger
from books.serializers import TicketDirectionSerializer, TicketSerializer, DirectionSerializer
from buses.models import Bus
from trips.models import Direction


# Create your views here.
class DirectionDates(APIView):
    def get(self, request):
        from_point = request.GET.get('from_point')
        to_point = request.GET.get('to_point')

        if not (from_point and to_point):
            return Response("Need from_point and to_point", status=status.HTTP_400_BAD_REQUEST)

        directions = Direction.objects.filter(
            from_point=from_point,
            to_point=to_point,
            from_datetime__gte=datetime.datetime.now()
        ).order_by('from_datetime__date', 'price')

        # Dictionary to keep track of the minimum price per date
        min_price_per_date = {}

        for direction in directions:
            direction_date = direction.from_datetime.date()
            if direction.free_places_count() > 0:
                if direction_date not in min_price_per_date:
                    min_price_per_date[direction_date] = direction
                elif direction.price < min_price_per_date[direction_date].price:
                    min_price_per_date[direction_date] = direction

        # Convert the dictionary to a list of dictionaries for the context
        directions_with_free_seats = [
            {'date': date, 'price': dir_obj.price}
            for date, dir_obj in min_price_per_date.items()
        ]

        return Response(directions_with_free_seats, status=status.HTTP_200_OK)


class GetTicket(APIView):
    def get(self, request):
        from_point = request.GET.get('from_point')
        to_point = request.GET.get('to_point')
        date_str = request.GET.get('date')
        passenger_count = int(request.GET.get('passenger_count'))

        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')

        directions = Direction.objects.filter(
            from_point=from_point,
            to_point=to_point,
            from_datetime__date=date,
        ).order_by("price")

        available_dirs = []
        for direction in directions:
            if direction.free_places_count() >= passenger_count:
                available_dirs.append(direction)

        serializer = TicketDirectionSerializer(available_dirs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DirectionPlaces(APIView):
    def get(self, request):
        direction_id = request.GET.get('direction_id')
        direction = Direction.objects.get(id=direction_id)
        tickets = Ticket.objects.filter(direction=direction).filter(Q(status="Payed") | Q(status="Booked"))
        print(tickets)
        ticket_places = TicketPassenger.objects.filter(ticket__in=tickets).values('place_num', 'place_floor')
        tickets_list = {
            "places_count": direction.bus.count_of_seats,
            "floors_count": direction.bus.floors,
            "busy_tickets": list(ticket_places)
        }
        return Response(tickets_list, status=status.HTTP_200_OK)


class CreateTicket(APIView):
    def post(self, request):
        serializer = TicketSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.create(serializer.validated_data)
            except Exception as e:
                print(e)
                return Response(e.__str__(), status=status.HTTP_400_BAD_REQUEST)
            return Response("OK", status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response("NOT OK", status=status.HTTP_400_BAD_REQUEST)


class DirectionListView(APIView):
    def get(self, request):
        directions = Direction.objects.all()
        serializer = DirectionSerializer(directions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)