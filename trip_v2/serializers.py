from rest_framework import serializers
from .models import Route, Stop, City

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'region']

    def create(self, validated_data):
        return City.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.region = validated_data.get('region', instance.region)
        instance.save()
        return instance

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id', 'name', 'travel_time_from_start', 'stop_time']

    def create(self, validated_data):
        return Stop.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.travel_time_from_start = validated_data.get('travel_time_from_start', instance.travel_time_from_start)
        instance.stop_time = validated_data.get('stop_time', instance.stop_time)
        instance.save()
        return instance

class RouteSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True)

    class Meta:
        model = Route
        fields = ['id', 'start_city', 'end_city', 'total_travel_time', 'created_at', 'stops']

    def create(self, validated_data):
        stops_data = validated_data.pop('stops')
        route = Route.objects.create(**validated_data)
        for stop_data in stops_data:
            Stop.objects.create(route=route, **stop_data)
        return route

    def update(self, instance, validated_data):
        stops_data = validated_data.pop('stops')
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
            else:
                Stop.objects.create(route=instance, **stop_data)
        return instance
