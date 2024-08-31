import datetime
import json

from django.db import connection
from django.db.models import Min, F, Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from trip.models import Trip
from trip_v2.models import Route, Stop
from books.models import Ticket, TicketPassenger
from books.serializers import TicketDirectionSerializer, TicketSerializer, TicketDetailSerializer
from buses.models import Bus


# Create your views here.
class DirectionDates(APIView):
    def get(self, request):
        from_city_id = request.GET.get('from_point')
        to_city_id = request.GET.get('to_point')

        if not (from_city_id and to_city_id):
            return Response({"error": "Need from_point and to_point"}, status=status.HTTP_400_BAD_REQUEST)

        # Assuming you have a mapping or a way to get city names from city IDs
        routes = Route.objects.filter(
            start_city_id=from_city_id,  # Filter by city ID
            end_city_id=to_city_id       # Filter by city ID
        ).order_by('created_at')

        if not routes.exists():
            return Response({"message": "No routes found between the specified cities"}, status=status.HTTP_404_NOT_FOUND)

        tickets_data = []
        for route in routes:
            trips = Trip.objects.filter(route=route)
            for trip in trips:
                serializer = TicketDirectionSerializer(trip)
                tickets_data.append(serializer.data)

        return Response(tickets_data, status=status.HTTP_200_OK)

class GetTicket(APIView):
    def get(self, request):
        from_city_id = request.GET.get('from')
        to_city_id = request.GET.get('to')
        date_str = request.GET.get('date')
        passenger_count = int(request.GET.get('passenger_count'))

        if not (from_city_id and to_city_id and date_str):
            return Response({"error": "from, to, and date are required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the date string to a date object
        try:
            travel_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Expected YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter routes based on the cities
        routes = Route.objects.filter(
            start_city_id=from_city_id,
            end_city_id=to_city_id
        ).order_by("total_travel_time")

        available_trips = []
        for route in routes:
            trips = Trip.objects.filter(
                route=route,
                start_date__lte=travel_date,  # Ensure the trip is scheduled on or before the travel date
                end_date__gte=travel_date      # Ensure the trip is ongoing on or after the travel date
            )

            for trip in trips:
                if trip.bus.count_of_seats >= passenger_count:  # Ensure there are enough seats
                    available_trips.append(trip)

        if not available_trips:
            return Response([], status=status.HTTP_200_OK)  # Return an empty list if no trips match

        # Serialize the available trips
        serializer = TicketDirectionSerializer(available_trips, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DirectionPlaces(APIView):
    def get(self, request):
        route_id = request.GET.get('direction_id')

        # Fetch the Trip instances associated with this route_id
        trips = Trip.objects.filter(route_id=route_id)

        # Now filter tickets by these trips
        tickets = Ticket.objects.filter(direction__in=trips).filter(Q(status="Payed") | Q(status="Booked"))

        ticket_places = TicketPassenger.objects.filter(ticket__in=tickets).values('place_num', 'place_floor')
        tickets_list = {
            "places_count": tickets.count(),
            "busy_tickets": list(ticket_places)
        }
        return Response(tickets_list, status=status.HTTP_200_OK)


class CreateTicket(APIView):
    def post(self, request):
        serializer = TicketSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                ticket, reserved_places = serializer.create(serializer.validated_data)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": "OK",
                "ticket_id": ticket.id,
                "reserved_places": reserved_places
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DirectionListView(APIView):
    def get(self, request):
        directions = Trip.objects.all()
        serializer = Trip(directions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RetrievePaidTicket(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            ticket = Ticket.objects.filter(user=user, status="Payed").first()
            if not ticket:
                return Response({"detail": "No paid ticket found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = TicketDetailSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)