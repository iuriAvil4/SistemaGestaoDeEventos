from django.forms import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from core.permissions import IsAdminUser, IsOrganizerUser, IsParticipantUser
from tickets.services.ticket_services import TicketService
from tickets.services.ticket_type_services import TicketTypeService
from tickets.models import Ticket, TicketType
from .serializer import TicketSerializer, TicketRegisterSerializer, TicketTypeRegisterSerializer
from rest_framework import status

# Ticket Views
class TicketListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminUser | IsOrganizerUser]
    serializer_class = TicketRegisterSerializer

    def get_queryset(self):
        return TicketService.get_all_tickets()

    def perform_create(self, serializer):
        ticket = TicketService.create_ticket(serializer.validated_data)
        TicketService.change_ticket_status(ticket, 'PENDING_PAYMENT')


class TicketDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser | IsOrganizerUser]
    serializer_class = TicketRegisterSerializer

    def get_queryset(self):
        return TicketService.get_all_tickets()

    def perform_update(self, serializer):
        ticket = self.get_object()
        TicketService.update_ticket(ticket, serializer.validated_data)

        new_status = serializer.validated_data.get('status')
        if new_status:
            TicketService.change_ticket_status(ticket, new_status)

    def perform_destroy(self, instance):
        TicketService.delete_ticket(instance)

        TicketService.change_ticket_status(instance, 'CANCELED')


class BuyerTicketsListView(APIView):
    permission_classes = [IsAdminUser | IsParticipantUser]

    def get(self, request):
        tickets = TicketService.get_tickets_by_buyer(request.user.id)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)


# TicketType Views
class TicketTypeListCreateView(ListCreateAPIView):
    permission_classes = [IsAdminUser | IsOrganizerUser]
    serializer_class = TicketTypeRegisterSerializer

    def get_queryset(self):
        return TicketTypeService.get_all_ticket_types()

    def perform_create(self, serializer):
        TicketTypeService.create_ticket_type(serializer.validated_data)


class TicketTypeDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser | IsOrganizerUser]
    serializer_class = TicketTypeRegisterSerializer

    def get_queryset(self):
        return TicketTypeService.get_all_ticket_types()

    def perform_update(self, serializer):
        ticket_type = self.get_object()
        TicketTypeService.update_ticket_type(ticket_type, serializer.validated_data)

    def perform_destroy(self, instance):
        TicketTypeService.delete_ticket_type(instance)


class PayTicketView(APIView):
    permission_classes = [IsAdminUser | IsOrganizerUser | IsParticipantUser]

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(pk=ticket_id, buyer=request.user)
            TicketService.pay_ticket(ticket)
            return Response({"detail": "Ticket payment successful."}, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"detail": "Ticket not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UseTicketView(APIView):
    permission_classes = [IsAdminUser | IsOrganizerUser | IsParticipantUser]

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(pk=ticket_id, buyer=request.user)
            TicketService.use_ticket(ticket)
            return Response({"detail": "Ticket used successfully."}, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"detail": "Ticket not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)