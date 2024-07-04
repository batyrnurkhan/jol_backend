import datetime
import json

from django.db.models import Min, F
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
            if direction.is_free():
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
