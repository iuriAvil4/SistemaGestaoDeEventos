from django.urls import path
from .views import (
    EventListCreateView,
    EventDetailView,
    OrganizerEventListView,
    CategoryListCreateView,
    CategoryDetailView
)

urlpatterns = [
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('events/organizer/', OrganizerEventListView.as_view(), name='organizer-event-list'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]
