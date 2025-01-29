from django.db.models import QuerySet
from .models import Event, Category

class EventService:
    @staticmethod
    def get_all_events() -> QuerySet:
        return Event.objects.select_related('organizer').prefetch_related('categories').all().order_by('title')
    
    @staticmethod
    def get_events_by_organizer(user) -> QuerySet:
        return Event.objects.filter(organizer=user).select_related('organizer').prefetch_related('categories')
    
    @staticmethod
    def get_event_by_id(event_id: int) -> Event:
        return Event.objects.select_related('organizer').prefetch_related('categories').get(pk=event_id)
    
    @staticmethod
    def create_event(validated_data, organizer) -> Event:
        validated_data['organizer'] = organizer
        return Event.objects.create(**validated_data)
    
    @staticmethod
    def update_event(event, validated_data) -> Event:
        for key, value in validated_data.items():
            setattr(event, key, value)
        event.save()
        return event
    
    @staticmethod
    def delete_event(event) -> None:
        event.delete()


class CategoryService:
    @staticmethod
    def get_all_categories() -> QuerySet:
        return Category.objects.all().order_by('name')
    
    @staticmethod
    def get_category_by_id(category_id: int) -> Category:
        return Category.objects.get(pk=category_id)
    
    @staticmethod
    def create_category(validated_data) -> Category:
        return Category.objects.create(**validated_data)
    
    @staticmethod
    def update_category(category, validated_data) -> Category:
        for key, value in validated_data.items():
            setattr(category, key, value)
        category.save()
        return category
    
    @staticmethod
    def delete_category(category) -> None:
        category.delete()
