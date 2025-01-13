from django.urls import path
from .views import create_event, create_category, list_events, update_event, delete_event, list_organizer_events, list_categories, update_category, delete_category
urlpatterns = [
    path('list_organizer_events/', list_organizer_events),

    path('create_event/', create_event),
    path('list_events/', list_events),
    path('update_event/<int:id>', update_event),
    path('delete_event/<int:id>', delete_event),

    path('create_category/', create_category),
    path('list_categories/', list_categories),
    path('update_category/<int:id>', update_category),
    path('delete_category/<int:id>', delete_category),
]
