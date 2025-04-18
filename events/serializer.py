from rest_framework import serializers
from django.utils.text import slugify
from .models import Event, Category

class EventRegisterSerializer(serializers.ModelSerializer):
    organizer = serializers.PrimaryKeyRelatedField(read_only=True)
    slug = serializers.CharField(read_only=True)
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        many=True
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "start_date",
            "end_date",
            "location",
            "total_capacity",
            "organizer",
            "categories",
            "event_status",
        ]

    def create(self, validated_data):
        request = self.context.get('request')  
        if request and hasattr(request, "user"):
            validated_data['organizer'] = request.user
        title = validated_data.get('title', '')
        validated_data['slug'] = slugify(title)
        return super().create(validated_data)

    def validate(self, data):
        instance = getattr(self, 'instance', None) 
        if instance:
            if instance.event_status == 'FINISHED':  
                if data.get('event_status') != 'FINISHED' or len(data) > 1:
                    raise serializers.ValidationError(
                        "Cannot modify other fields of a completed event."
                    )
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