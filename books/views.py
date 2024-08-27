import datetime
import json

from django.db.models import Min, F, Q
from django.shortcuts import render
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from trip_v2.models import Route, Stop
from books.models import Ticket, TicketPassenger
from books.serializers import TicketDirectionSerializer, TicketSerializer, TicketDetailSerializer
from buses.models import Bus


# Create your views here.
class DirectionDates(APIView):
    def get(self, request):
        from_city = request.GET.get('from_point')
        to_city = request.GET.get('to_point')

        if not (from_city and to_city):
            return Response("Need from_point and to_point", status=status.HTTP_400_BAD_REQUEST)

        routes = Route.objects.filter(
            start_city=from_city,
            end_city=to_city,
            created_at__gte=datetime.datetime.now()
        ).order_by('created_at', 'total_travel_time')

        # Dictionary to keep track of the minimum travel time per route
        min_time_per_route = {}

        for route in routes:
            if route.stops.exists():
                if route not in min_time_per_route:
                    min_time_per_route[route] = route
                elif route.total_travel_time < min_time_per_route[route].total_travel_time:
                    min_time_per_route[route] = route

        # Convert the dictionary to a list of dictionaries for the context
        routes_with_times = [
            {'date': route.created_at.date(), 'total_travel_time': route.total_travel_time}
            for route in min_time_per_route.values()
        ]

        return Response(routes_with_times, status=status.HTTP_200_OK)


class GetTicket(APIView):
    def get(self, request):
        from_city = request.GET.get('from_point')
        to_city = request.GET.get('to_point')
        date_str = request.GET.get('date')
        passenger_count = int(request.GET.get('passenger_count'))

        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')

        routes = Route.objects.filter(
            start_city=from_city,
            end_city=to_city,
            created_at__date=date,
        ).order_by("total_travel_time")

        available_routes = []
        for route in routes:
            if route.stops.count() >= passenger_count:
                available_routes.append(route)

        serializer = TicketDirectionSerializer(available_routes, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



class DirectionPlaces(APIView):
    def get(self, request):
        route_id = request.GET.get('direction_id')
        route = Route.objects.get(id=route_id)
        tickets = Ticket.objects.filter(direction=route).filter(Q(status="Payed") | Q(status="Booked"))

        ticket_places = TicketPassenger.objects.filter(ticket__in=tickets).values('place_num', 'place_floor')
        tickets_list = {
            "places_count": route.stops.count(),
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
        directions = Direction.objects.all()
        serializer = DirectionSerializer(directions, many=True)
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