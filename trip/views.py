import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from books.models import TicketPassenger
from .models import Trip
from .serializers import TripSerializer
import datetime

# Initialize logger for trip app
logger = logging.getLogger('trip')


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    @action(detail=False, methods=['get'], url_path='get-trips')
    def get_trips(self, request):
        from_city = request.query_params.get('from_city')
        to_city = request.query_params.get('to_city')
        date_str = request.query_params.get('date')

        if not from_city or not to_city or not date_str:
            return Response({"error": "from_city, to_city, and date are required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            travel_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Expected YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter trips based on cities and date
        trips = Trip.objects.filter(route__start_city_id=from_city, route__end_city_id=to_city, start_date=travel_date)

        if trips.exists():
            serializer = TripSerializer(trips, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No trips available for the selected route and date."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        trip = self.get_object()
        logger.info(f"Toggling active status for Trip ID {trip.id}. Current status: {trip.status}")

        trip.active = not trip.active
        trip.save()

        logger.info(f"Active status for Trip ID {trip.id} updated to {trip.active}")
        return Response({'status': 'active status updated', 'active': trip.active})

    @action(detail=True, methods=['get'], url_path='trip-details-with-seats')
    def get_trip_details_with_seats(self, request, pk=None):
        try:
            trip = self.get_object()
            serializer = self.get_serializer(trip)
            trip_data = serializer.data

            # Fetch all seats for the bus related to this trip
            bus_seats = [
                {
                    "seatId": seat['seat_id'],
                    "seatCol": seat['seat_col'],
                    "seatRow": seat['seat_row'],
                    "seatType": seat['seat_type']
                } for seat in trip.bus.seats.all().values('seat_id', 'seat_col', 'seat_row', 'seat_type')
            ]

            # Fetch all booked seats for the trip
            booked_seats = TicketPassenger.objects.filter(ticket__direction=trip).values('place_num', 'place_floor')

            # Mark booked seats
            for seat in bus_seats:
                for booked in booked_seats:
                    if seat['seatId'] == booked['place_num']:
                        seat['isBooked'] = True
                        break
                else:
                    seat['isBooked'] = False

            trip_data['seats'] = bus_seats

            return Response(trip_data, status=status.HTTP_200_OK)

        except Trip.DoesNotExist:
            logger.error(f"Trip ID {pk} not found")
            return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)
