from datetime import timezone
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsAdminUser, IsOrganizerUser, IsParticipantUser
from .models import Ticket, TicketType
from events.models import Event
from users.models import User
from .serializer import TicketTypeRegisterSerializer, TicketSerializer, TicketRegisterSerializer, TicketTypeSerializer
    

@api_view(['POST'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def create_ticket_type(request):
    data = request.data.copy()
    event_id = data.get("event")
    if not event_id:
        return Response({"detail": "The 'event' field is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        event = Event.objects.get(pk=event_id)
        if event.event_status != 'PUBLISHED':
            return Response({"detail": f"Event with ID {event_id} is not published."}, status=status.HTTP_400_BAD_REQUEST)
    except Event.DoesNotExist:
        return Response({"detail": f"Event with ID {event_id} not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = TicketTypeRegisterSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        ticket_type = serializer.save(event=event)
        response_serializer = TicketTypeRegisterSerializer(ticket_type)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def list_ticket_types(request):
    ticket_types = TicketType.objects.all().order_by("id")
    serializer = TicketTypeSerializer(ticket_types, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def update_ticket_type(request, id):
    try:
        ticket_type = TicketType.objects.get(pk=id)
    except TicketType.DoesNotExist:
        return Response(
            {"error": f"TicketType with id {id} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = TicketTypeRegisterSerializer(ticket_type, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def delete_ticket_type(request, id):
    try:
        ticket_type = TicketType.objects.get(pk=id)
        ticket_type.delete()
        return Response({"message": f"TicketType with id {id} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except TicketType.DoesNotExist:
        return Response(
            {"error": f"TicketType with id {id} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    

#-----------------------------------------------------------------------------------------------------------------------


@api_view(['POST'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def create_ticket(request):
    data = request.data.copy()
    id_ticket_type = data.get("ticket_type")
    id_buyer = data.get("buyer")
    
    if not id_ticket_type or not id_buyer:
        return Response({"detail": "Os campos 'ticket_type' e 'buyer' são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)


    try:
        ticket_type = TicketType.objects.get(pk=id_ticket_type)
        buyer = User.objects.get(pk=id_buyer)
    except TicketType.DoesNotExist:
        return Response({"detail": f"TicketType com ID {id_ticket_type} não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"detail": f"User com ID {id_buyer} não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    if Ticket.objects.filter(ticket_type=ticket_type, buyer=buyer).exists():
        return Response({"detail": "O usuário já possui um ticket deste tipo para este evento."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        ticket_type.reserve_ticket()
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = TicketRegisterSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        ticket = serializer.save(ticket_type=ticket_type, buyer=buyer)
        response_serializer = TicketRegisterSerializer(ticket)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    ticket_type.release_ticket()
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def list_tickets(request):
    tickets = Ticket.objects.all().order_by("id")
    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def list_tickets_by_buyer(request, id):
    try:
        tickets = Ticket.objects.filter(buyer=id)  
        if not tickets.exists():
            return Response(
                {"error": f"No tickets found for buyer with ID {id}."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TicketSerializer(tickets, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser | IsParticipantUser])
def list_user_tickets(request):
    user = request.user
    tickets = Ticket.objects.filter(buyer=user) 
    serializer = TicketSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def update_ticket(request, id):
    try:
        ticket = Ticket.objects.get(pk=id)
    except Ticket.DoesNotExist:
        return Response(
            {"error": f"Ticket with id {id} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = TicketRegisterSerializer(ticket, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def delete_ticket(request, id):
    try:
        ticket_type = Ticket.objects.get(pk=id)
        ticket_type.delete()
        return Response({"message": f"Ticket with id {id} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Ticket.DoesNotExist:
        return Response(
            {"error": f"Ticket with id {id} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser | IsParticipantUser])
def generate_ticket_qr(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
        if not request.user.is_staff and ticket.buyer != request.user:
            return Response({"detail": "Você não tem permissão para acessar este ticket."}, status=status.HTTP_403_FORBIDDEN)
        qr_response = ticket.generate_qr_response()
        return qr_response  
    except Ticket.DoesNotExist:
        return Response({"detail": f"Ticket com ID {ticket_id} não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Ocorreu um erro: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


#----------------------------------------------------------------------------------------------------------------------------

@api_view(['DELETE'])
@permission_classes([IsAdminUser | IsOrganizerUser | IsParticipantUser])
def cancel_ticket(request, id):
    try:
        ticket = Ticket.objects.get(pk=id)
        if not request.user.is_staff and ticket.buyer != request.user:
            return Response({"detail": "Você não tem permissão para cancelar este ticket."}, status=status.HTTP_403_FORBIDDEN)
        
        ticket.change_ticket_status('CANCELED')
        ticket.ticket_type.release_ticket()
    
        return Response({"message": f"Ticket with id {id} canceled successfully."}, status=status.HTTP_200_OK)
    except Ticket.DoesNotExist:
        return Response(
            {"error": f"Ticket with id {id} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response({"error": f"Ocorreu um erro: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAdminUser | IsOrganizerUser | IsParticipantUser])
def use_ticket(request, id):
    try:
        ticket = Ticket.objects.get(pk=id)
        if not request.user.is_staff and ticket.buyer != request.user:
            return Response({"detail": "Você não tem permissão para usar este ticket."}, status=status.HTTP_403_FORBIDDEN)

        ticket.change_ticket_status('USED')

        return Response({"message": f"Ticket with id {id} used successfully."}, status=status.HTTP_200_OK)
    except Ticket.DoesNotExist:
        return Response({"error": f"Ticket with id {id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Ocorreu um erro: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAdminUser | IsOrganizerUser | IsParticipantUser])
def pay_ticket(request, id):
    try:
        ticket = Ticket.objects.get(pk=id)
        ticket.change_ticket_status('ACTIVE')
        return Response({"message": f"Ticket with id {id} paid successfully."}, status=status.HTTP_200_OK)
    except Ticket.DoesNotExist:
        return Response({"error": f"Ticket with id {id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Ocorreu um erro: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
