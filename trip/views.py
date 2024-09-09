import logging
from rest_framework import viewsets
from .models import Trip
from .serializers import TripSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

# Initialize logger for trip app
logger = logging.getLogger('trip')


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        trip = self.get_object()
        logger.info(f"Toggling active status for Trip ID {trip.id}. Current status: {trip.status}")

        trip.active = not trip.active
        trip.save()

        logger.info(f"Active status for Trip ID {trip.id} updated to {trip.active}")
        return Response({'status': 'active status updated', 'active': trip.active})
