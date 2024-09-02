import logging
from rest_framework import serializers
from .models import Route, Stop, City

# Initialize logger for trip_v2 app
logger = logging.getLogger('trip_v2')

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'region']

    def create(self, validated_data):
        logger.info(f"Creating City with data: {validated_data}")
        city = City.objects.create(**validated_data)
        logger.debug(f"City created with ID: {city.id}")
        return city

    def update(self, instance, validated_data):
        logger.info(f"Updating City ID {instance.id} with data: {validated_data}")
        instance.name = validated_data.get('name', instance.name)
        instance.region = validated_data.get('region', instance.region)
        instance.save()
        logger.debug(f"City ID {instance.id} updated")
        return instance

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id', 'name', 'travel_time_from_start', 'stop_time']

    def create(self, validated_data):
        logger.info(f"Creating Stop with data: {validated_data}")
        stop = Stop.objects.create(**validated_data)
        logger.debug(f"Stop created with ID: {stop.id}")
        return stop

    def update(self, instance, validated_data):
        logger.info(f"Updating Stop ID {instance.id} with data: {validated_data}")
        instance.name = validated_data.get('name', instance.name)
        instance.travel_time_from_start = validated_data.get('travel_time_from_start', instance.travel_time_from_start)
        instance.stop_time = validated_data.get('stop_time', instance.stop_time)
        instance.save()
        logger.debug(f"Stop ID {instance.id} updated")
        return instance

class RouteSerializer(serializers.ModelSerializer):
    start_city = CitySerializer(read_only=True)  # Include full start city details
    end_city = CitySerializer(read_only=True)  # Include full end city details
    stops = StopSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'start_city', 'end_city', 'total_travel_time', 'created_at', 'stops']

    def create(self, validated_data):
        stops_data = validated_data.pop('stops', [])
        logger.info(f"Creating Route with data: {validated_data} and stops: {stops_data}")
        route = Route.objects.create(**validated_data)
        for stop_data in stops_data:
            Stop.objects.create(route=route, **stop_data)
        logger.debug(f"Route created with ID: {route.id}")
        return route

    def update(self, instance, validated_data):
        stops_data = validated_data.pop('stops', [])
        logger.info(f"Updating Route ID {instance.id} with data: {validated_data}")
        instance.start_city = validated_data.get('start_city', instance.start_city)
        instance.end_city = validated_data.get('end_city', instance.end_city)
        instance.total_travel_time = validated_data.get('total_travel_time', instance.total_travel_time)
        instance.save()

        for stop_data in stops_data:
            stop_id = stop_data.get('id')
            if stop_id:
                stop = Stop.objects.get(id=stop_id, route=instance)
                stop.name = stop_data.get('name', stop.name)
                stop.travel_time_from_start = stop_data.get('travel_time_from_start', stop.travel_time_from_start)
                stop.stop_time = stop_data.get('stop_time', stop.stop_time)
                stop.save()
                logger.debug(f"Updated Stop ID {stop.id} for Route ID {instance.id}")
            else:
                Stop.objects.create(route=instance, **stop_data)
                logger.debug(f"Created new Stop for Route ID {instance.id}")
        return instance
