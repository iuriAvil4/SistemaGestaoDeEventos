from datetime import timedelta
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.utils.timezone import now
from tickets.models import Ticket
from tickets.services.ticket_type_services import TicketTypeService
from django.conf import settings
from django.core.mail import EmailMessage

@shared_task(
        autoretry_for=(Exception,),
        retry_kwargs={"max_retries": 5, "countdown": 10},
)
def clear_expired_reservations():
    """
    Remove reservas que expiraram sem pagamento.
    """
    try:
        expired_tickets = Ticket.objects.filter(ticket_status='PENDING_PAYMENT', bought_at__lt=now() - timedelta(minutes=15))
        
        for ticket in expired_tickets:
            TicketTypeService.release_ticket(ticket.ticket_type)
            ticket.delete()

        return f"Reservas expiradas limpas: {expired_tickets.count()}"
    except Exception as e:
        raise e

@shared_task(rate_limit="5/m")
def send_custom_email(subject, message, recipient_list, attachments=None):
    """
    Envia um e-mail com anexos usando as configurações do Django.
    
    :param subject: Assunto do e-mail
    :param message: Corpo do e-mail
    :param recipient_list: Lista de destinatários (ex: ['email1@email.com'])
    :param attachments: Lista de anexos [(nome_arquivo, conteudo, tipo_mime)]
    """
    email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, recipient_list)
    
    if attachments:
        for attachment in attachments:
            filename, content, mime_type = attachment
            email.attach(filename, content, mime_type)

    email.send()
