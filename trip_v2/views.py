from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Route, City
from .serializers import RouteSerializer, CitySerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class CityListView(APIView):
    def get(self, request):
        cities = City.objects.all()  # Retrieve all cities from the database
        serializer = CitySerializer(cities, many=True)  # Serialize the data
        return Response(serializer.data)