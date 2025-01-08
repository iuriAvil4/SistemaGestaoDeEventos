from rest_framework import serializers
from .models import Event, Category

class EventRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'start_date', 'end_date',
            'location', 'total_capacity', 'event_status', 'organizer', 'categories'
        ]

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("The start date must be before the end date.")
        if data['total_capacity'] < 1:
            raise serializers.ValidationError("The total capacity must be greater than zero.")
        return data
    

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'start_date', 'end_date',
            'location', 'total_capacity', 'event_status', 'organizer', 'categories'
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'category_status']