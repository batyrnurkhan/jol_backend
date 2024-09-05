import logging
from rest_framework import viewsets
from .models import Trip
from .serializers import TripCreateUpdateSerializer, TripDetailSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

# Initialize logger for trip app
logger = logging.getLogger('trip')


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()

    def get_serializer_class(self):
        """
        Return the appropriate serializer based on the request method.
        """
        if self.request.method in ['GET']:
            return TripDetailSerializer  # Use this serializer for GET requests (list, retrieve)
        return TripCreateUpdateSerializer  # Use this serializer for POST, PUT, PATCH

    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        trip = self.get_object()
        logger.info(f"Toggling active status for Trip ID {trip.id}. Current status: {trip.status}")

        # Toggle active status
        trip.active = not trip.active
        trip.save()

        logger.info(f"Active status for Trip ID {trip.id} updated to {trip.active}")
        return Response({'status': 'active status updated', 'active': trip.active})
