from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from core.permissions import IsAdminUser, IsOrganizerUser, IsParticipantUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import EventService, CategoryService
from .serializer import EventSerializer, EventRegisterSerializer, CategorySerializer


# Event Views
class EventListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminUser | IsOrganizerUser]
    serializer_class = EventRegisterSerializer

    def get_queryset(self):
        return EventService.get_all_events()

    def perform_create(self, serializer):
        EventService.create_event(serializer.validated_data, self.request.user)


class EventDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser | IsOrganizerUser]
    serializer_class = EventRegisterSerializer

    def get_queryset(self):
        return EventService.get_all_events()

    def perform_update(self, serializer):
        event = self.get_object()
        EventService.update_event(event, serializer.validated_data)

    def perform_destroy(self, instance):
        EventService.delete_event(instance)


class OrganizerEventListView(APIView):
    permission_classes = [IsAdminUser | IsOrganizerUser]

    def get(self, request):
        events = EventService.get_events_by_organizer(request.user)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)


# Category Views
class CategoryListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return CategoryService.get_all_categories()

    def perform_create(self, serializer):
        CategoryService.create_category(serializer.validated_data)


class CategoryDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return CategoryService.get_all_categories()

    def perform_update(self, serializer):
        category = self.get_object()
        CategoryService.update_category(category, serializer.validated_data)

    def perform_destroy(self, instance):
        CategoryService.delete_category(instance)
