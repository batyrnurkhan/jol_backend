import logging
from rest_framework import viewsets
from rest_framework.views import APIView

from books.models import TicketPassenger, Ticket
from trip.models import Trip
from .models import Bus, Driver, Seat
from .serializers import BusListSerializer, BusCreateSerializer, DriverListSerializer, DriverCreateUpdateSerializer, \
    SeatSerializer
from rest_framework.response import Response
from rest_framework import status

# Initialize logger for buses app
logger = logging.getLogger('buses')

class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            logger.debug(f"Using BusListSerializer for action: {self.action}")
            return BusListSerializer
        logger.debug(f"Using BusCreateSerializer for action: {self.action}")
        return BusCreateSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating a new bus with data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bus = serializer.save()

        # Clear any existing seats (just to be safe)
        Seat.objects.filter(bus=bus).delete()

        # Create seats for the bus
        seats_data = request.data.get('seats', [])
        for seat_data in seats_data:
            Seat.objects.get_or_create(bus=bus, **seat_data)  # Ensure no duplication

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating bus with data: {request.data}")
        bus = self.get_object()
        serializer = self.get_serializer(bus, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Update seats for the bus
        Seat.objects.filter(bus=bus).delete()  # Clear existing seats
        seats_data = request.data.get('seats', [])
        for seat_data in seats_data:
            Seat.objects.get_or_create(bus=bus, **seat_data)  # Prevent duplication during update

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        bus_id = self.get_object().id
        logger.info(f"Deleting bus with ID: {bus_id}")
        return super().destroy(request, *args, **kwargs)


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            logger.debug(f"Using DriverListSerializer for action: {self.action}")
            return DriverListSerializer
        logger.debug(f"Using DriverCreateUpdateSerializer for action: {self.action}")
        return DriverCreateUpdateSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating a new driver with data: {request.data}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating driver with data: {request.data}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        driver_id = self.get_object().id
        logger.info(f"Deleting driver with ID: {driver_id}")
        return super().destroy(request, *args, **kwargs)


class BusSeatView(APIView):
    def post(self, request):
        trip_id = request.data.get('trip_id')

        if not trip_id:
            return Response({"error": "Trip ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the trip by ID
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the bus associated with the trip
        bus = trip.bus

        # Get the seats of the bus
        seats = Seat.objects.filter(bus=bus)

        # Fetch all tickets for this trip
        tickets = Ticket.objects.filter(direction=trip, status__in=['Booked', 'Bought'])

        # Get all the booked or bought seats
        booked_seats = TicketPassenger.objects.filter(ticket__in=tickets).values_list('place_num', flat=True)

        # Prepare seat data with the status
        seat_data = []
        for seat in seats:
            seat_status = 'free'
            if seat.seat_id in booked_seats:
                seat_status = 'booked' if tickets.filter(ticketpassenger__place_num=seat.seat_id,
                                                         status='Booked').exists() else 'bought'

            seat_data.append({
                "seat_id": seat.seat_id,
                "seat_col": seat.seat_col,
                "seat_row": seat.seat_row,
                "seat_type": seat.seat_type,
                "status": seat_status
            })

        # Return the seat data
        return Response({
            'bus': bus.name,
            'seats': seat_data
        }, status=status.HTTP_200_OK)