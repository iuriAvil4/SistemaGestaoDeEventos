from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Count
from rest_framework.decorators import api_view, permission_classes
from core.permissions import IsAdminUser, IsOrganizerUser, IsParticipantUser
from tickets.models import Ticket, TicketType
from events.models import Event


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def ticket_sales_report(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    ticket_types = TicketType.objects.filter(event=event)
    
    report_data = []
    for ticket_type in ticket_types:
        tickets_sold = Ticket.objects.filter(ticket_type=ticket_type).exclude(ticket_status=Ticket.TicketStatusChoices.PENDING_PAYMENT).count()
        
        revenue = Ticket.objects.filter(ticket_type=ticket_type).exclude(ticket_status=Ticket.TicketStatusChoices.PENDING_PAYMENT).aggregate(
            total_revenue=Sum('price_paid')
        )['total_revenue'] or 0.00
        
        report_data.append({
            'ticket_type_id': ticket_type.id,
            'ticket_type_name': ticket_type.name,
            'tickets_sold': tickets_sold,
            'revenue': float(revenue),
        })

    # Retorna os dados do relatório em formato JSON
    return JsonResponse({
        'event_id': event.id,
        'event_name': event.title,
        'ticket_sales_report': report_data,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def ticket_status_report(request, event_id):
    """
    Endpoint para obter um relatório de contagem total de tickets por tipo de ticket para um evento.
    
    Parâmetros:
        - event_id (int): ID do evento.
    
    Retorno:
        - JSON com a contagem total de tickets por tipo.
    """
    event = get_object_or_404(Event, pk=event_id)

    # Agrupa os tickets por tipo de ticket e calcula o total
    ticket_counts = (
        Ticket.objects.filter(ticket_type__event=event)
        .values('ticket_type__name')  # Usa o nome do tipo de ticket
        .annotate(total=Count('id'))  # Conta o número de tickets
    )

    # Converte os dados em uma lista formatada
    report_data = [
        {"ticket_type": ticket['ticket_type__name'], "total": ticket['total']}
        for ticket in ticket_counts
    ]

    # Retorna os dados do relatório em formato JSON
    return JsonResponse({
        'event_id': event.id,
        'event_name': event.title,
        'ticket_summary': report_data,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def event_attendance(request, event_id):
    """
    Endpoint para obter a taxa de participação em um evento com base nos tickets usados.
    
    Parâmetros:
        - event_id (int): ID do evento.
    
    Retorno:
        - JSON com o total de tickets emitidos, usados e a taxa de participação.
    """
    event = get_object_or_404(Event, pk=event_id)
    # Contar o número total de tickets emitidos para o evento
    total_tickets = Ticket.objects.filter(ticket_type__event=event).count()

    # Contar o número de tickets com status "USED" associados ao evento
    used_tickets = Ticket.objects.filter(ticket_type__event=event, ticket_status='USED').count()

    # Calcula a taxa de participação (attendance rate)
    attendance_rate = (used_tickets / total_tickets * 100) if total_tickets > 0 else 0

    return JsonResponse({
        'event_id': event.id,
        'event_name': event.title,
        "total_tickets": total_tickets, 
        "used_tickets": used_tickets, 
        "attendance_rate": attendance_rate
    })

@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def ticket_type_list_for_published_events(request):
    """
    Endpoint para obter uma lista de IDs e nomes dos tipos de tickets para eventos publicados.
    
    Retorno:
        - JSON contendo uma lista de tipos de tickets disponíveis em eventos publicados.
    """
    ticket_types = TicketType.objects.filter(event__event_status='PUBLISHED').values_list('id', 'name')

    return JsonResponse(list(ticket_types), safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def ticket_sales_detail(request):
    """
    Endpoint para obter um relatório detalhado de tickets vendidos, incluindo comprador e tipo de ticket.
    
    Retorno:
        - JSON contendo detalhes de cada ticket vendido.
    """
    tickets = Ticket.objects.select_related('buyer', 'ticket_type').filter(ticket_status='ACTIVE')

    # Construindo o relatório
    report_data = [
        {
            "ticket_id": ticket.id,
            "buyer": ticket.buyer.name,
            "ticket_type": ticket.ticket_type.name,
            "price_paid": ticket.price_paid
        }
        for ticket in tickets
    ]

    return JsonResponse(report_data, safe=False)


@api_view(['GET'])
@permission_classes([IsAdminUser | IsOrganizerUser])
def events_with_ticket_types(request):
    """
    Endpoint para obter um relatório de eventos com seus respectivos tipos de tickets.
    
    Retorno:
        - JSON contendo os eventos e os tipos de tickets disponíveis para cada um.
    """
    events = Event.objects.prefetch_related('ticket_types')

    report_data = [
        {
            "event_name": event.title,
            "ticket_types": [ticket_type.name for ticket_type in event.ticket_types.all()]
        }
        for event in events
    ]

    return JsonResponse(report_data, safe=False)
