from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from tickets.models import Ticket
from tickets.services.ticket_type_services import TicketTypeService
from django.core.mail import send_mail
from django.conf import settings

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

@shared_task
def send_custom_email(subject, message, recipient_list):
    """
    Envia um e-mail usando as configurações do Django.
    
    :param subject: Assunto do e-mail
    :param message: Corpo do e-mail
    :param recipient_list: Lista de destinatários (ex: ['email1@email.com', 'email2@email.com'])
    """
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)