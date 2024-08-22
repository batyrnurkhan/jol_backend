from rest_framework import viewsets
from .models import Trip
from .serializers import TripSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        trip = self.get_object()
        trip.active = not trip.active
        trip.save()
        return Response({'status': 'active status updated', 'active': trip.active})
