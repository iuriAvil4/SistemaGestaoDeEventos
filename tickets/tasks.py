from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from tickets.models import Ticket
from tickets.services.ticket_type_services import TicketTypeService

@shared_task
def clear_expired_reservations():
    """
    Remove reservas que expiraram sem pagamento.
    """
    expired_tickets = Ticket.objects.filter(ticket_status='PENDING_PAYMENT', bought_at__lt=now() - timedelta(minutes=15))
    
    for ticket in expired_tickets:
        TicketTypeService.release_ticket(ticket.ticket_type)
        ticket.delete()

    return f"Reservas expiradas limpas: {expired_tickets.count()}"
