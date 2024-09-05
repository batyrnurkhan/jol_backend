import logging
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
from trip.serializers import TripDetailSerializer
from trip_v2.models import Route, Stop
from books.models import Ticket, TicketPassenger
from books.serializers import TicketDirectionSerializer, TicketSerializer, TicketDetailSerializer
from buses.models import Bus

# Initialize logger for books app
logger = logging.getLogger('books')

class DirectionDates(APIView):
    def get(self, request):
        from_city_id = request.GET.get('from_point')
        to_city_id = request.GET.get('to_point')

        if not (from_city_id and to_city_id):
            logger.error("Missing from_point or to_point in request parameters")
            return Response({"error": "Need from_point and to_point"}, status=status.HTTP_400_BAD_REQUEST)

        routes = Route.objects.filter(
            start_city_id=from_city_id,
            end_city_id=to_city_id
        ).order_by('created_at')

        if not routes.exists():
            logger.warning(f"No routes found between cities {from_city_id} and {to_city_id}")
            return Response({"message": "No routes found between the specified cities"}, status=status.HTTP_404_NOT_FOUND)

        tickets_data = []
        for route in routes:
            trips = Trip.objects.filter(route=route)
            for trip in trips:
                serializer = TicketDirectionSerializer(trip)
                tickets_data.append(serializer.data)

        logger.info(f"Found {len(tickets_data)} trips for route from {from_city_id} to {to_city_id}")
        return Response(tickets_data, status=status.HTTP_200_OK)

class GetTicket(APIView):
    def get(self, request):
        from_city_id = request.GET.get('from')
        to_city_id = request.GET.get('to')
        date_str = request.GET.get('date')
        passenger_count = int(request.GET.get('passenger_count'))

        if not (from_city_id and to_city_id and date_str):
            logger.error("Missing required parameters: from, to, and date")
            return Response({"error": "from, to, and date are required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            travel_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.error(f"Invalid date format: {date_str}")
            return Response({"error": "Invalid date format. Expected YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        routes = Route.objects.filter(
            start_city_id=from_city_id,
            end_city_id=to_city_id
        ).order_by("total_travel_time")

        available_trips = []
        for route in routes:
            trips = Trip.objects.filter(
                route=route,
                start_date__lte=travel_date,
                end_date__gte=travel_date
            )

            for trip in trips:
                if trip.bus.count_of_seats >= passenger_count:
                    available_trips.append(trip)

        if not available_trips:
            logger.info(f"No available trips found from {from_city_id} to {to_city_id} on {date_str}")
            return Response([], status=status.HTTP_200_OK)

        serializer = TicketDirectionSerializer(available_trips, many=True)
        logger.info(f"Found {len(available_trips)} available trips from {from_city_id} to {to_city_id} on {date_str}")
        return Response(serializer.data, status=status.HTTP_200_OK)

class DirectionPlaces(APIView):
    def get(self, request):
        route_id = request.GET.get('direction_id')

        trips = Trip.objects.filter(route_id=route_id)
        tickets = Ticket.objects.filter(direction__in=trips).filter(Q(status="Payed") | Q(status="Booked"))

        ticket_places = TicketPassenger.objects.filter(ticket__in=tickets).values('place_num', 'place_floor')
        tickets_list = {
            "places_count": tickets.count(),
            "busy_tickets": list(ticket_places)
        }
        logger.info(f"Retrieved places for route ID: {route_id}")
        return Response(tickets_list, status=status.HTTP_200_OK)

class CreateTicket(APIView):
    def post(self, request):
        serializer = TicketSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                ticket, reserved_places = serializer.create(serializer.validated_data)
                logger.info(f"Ticket created successfully with ID: {ticket.id}")
            except ValidationError as e:
                logger.error(f"Validation error while creating ticket: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error while creating ticket: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": "OK",
                "ticket_id": ticket.id,
                "reserved_places": reserved_places
            }, status=status.HTTP_201_CREATED)

        logger.error(f"Invalid data received for creating ticket: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DirectionListView(APIView):
    def get(self, request):
        directions = Trip.objects.all()
        serializer = TripDetailSerializer(directions, many=True)
        logger.info(f"Retrieved list of directions. Count: {len(directions)}")
        return Response(serializer.data, status=status.HTTP_200_OK)

class RetrievePaidTicket(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            ticket = Ticket.objects.filter(user=user, status="Payed").first()
            if not ticket:
                logger.warning(f"No paid ticket found for user ID: {user.id}")
                return Response({"detail": "No paid ticket found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = TicketDetailSerializer(ticket)
            logger.info(f"Retrieved paid ticket with ID: {ticket.id} for user ID: {user.id}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error while retrieving paid ticket: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
