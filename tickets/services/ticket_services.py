from django.db.models import QuerySet
from django.forms import ValidationError
from django.db import transaction
from django.utils.timezone import now
from tickets.models import Ticket, TicketType
from tickets.services.ticket_type_services import TicketTypeService



class TicketService:
    @staticmethod
    def get_all_tickets() -> QuerySet:
        return Ticket.objects.select_related('ticket_type', 'buyer').all()

    @staticmethod
    def get_ticket_by_id(ticket_id: int) -> Ticket:
        return Ticket.objects.select_related('ticket_type', 'buyer').get(pk=ticket_id)

    @staticmethod
    def get_tickets_by_buyer(buyer_id: int) -> QuerySet:
        return Ticket.objects.filter(buyer_id=buyer_id).select_related('ticket_type', 'buyer')

    @staticmethod
    def create_ticket(validated_data) -> Ticket:
        ticket_type = validated_data.get('ticket_type')
        buyer = validated_data.get('buyer')

        if not ticket_type or not buyer:
            raise ValidationError("Both 'ticket_type' and 'buyer' fields are required.")

        TicketTypeService.reserve_ticket(ticket_type)

        try:
            ticket = Ticket.objects.create(**validated_data)
        except Exception:
            TicketTypeService.release_ticket(ticket_type)
            raise

        TicketService.change_ticket_status(ticket, 'PENDING_PAYMENT')
        return ticket

    @staticmethod
    def update_ticket(ticket: Ticket, validated_data) -> Ticket:
        for key, value in validated_data.items():
            setattr(ticket, key, value)
        ticket.save()
        return ticket

    @staticmethod
    def delete_ticket(ticket: Ticket) -> None:
        TicketTypeService.release_ticket(ticket.ticket_type)
        ticket.delete()

    @staticmethod
    def pay_ticket(ticket: Ticket) -> Ticket:
        TicketService.change_ticket_status(ticket, 'ACTIVE')
        ticket.payment_date = now() 
        ticket.save()
        return ticket

    @staticmethod
    def use_ticket(ticket: Ticket) -> Ticket:
        ticket.change_ticket_status('USED')
        ticket.used_at = now()  
        ticket.save()
        return ticket

    @staticmethod
    @transaction.atomic
    def change_ticket_status(ticket: Ticket, new_status: str) -> Ticket:
        valid_statuses = {'ACTIVE', 'INACTIVE', 'PENDING_PAYMENT', 'CANCELED', 'USED', 'EXPIRED'}

        if new_status not in valid_statuses:
            raise ValidationError(f"'{new_status}' is not a valid ticket status.")

        if ticket.ticket_status in {'CANCELED', 'USED'}:
            raise ValidationError(f"Cannot change status from '{ticket.ticket_status}' to '{new_status}'.")

        if new_status == 'USED' and ticket.ticket_status != 'ACTIVE':
            raise ValidationError("Only ACTIVE tickets can be marked as USED.")

        if new_status == 'ACTIVE' and ticket.ticket_status != 'PENDING_PAYMENT':
            raise ValidationError("Only PENDING_PAYMENT tickets can transition to ACTIVE.")

        if new_status == 'CANCELED' and ticket.ticket_status == 'PENDING_PAYMENT':
            TicketTypeService.release_ticket(ticket.ticket_type)

        ticket.ticket_status = new_status
        if new_status == 'USED':
            ticket.used_at = now()

        ticket.save()
        return ticket