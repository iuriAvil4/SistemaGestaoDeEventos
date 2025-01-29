from django.db.models import QuerySet
from django.forms import ValidationError
from tickets.models import TicketType
from events.models import Event
from django.db import transaction


class TicketTypeService:
    @staticmethod
    def get_all_ticket_types() -> QuerySet:
        return TicketType.objects.select_related('event').all()

    @staticmethod
    def get_ticket_type_by_id(ticket_type_id: int) -> TicketType:
        return TicketType.objects.get(pk=ticket_type_id)

    @staticmethod
    def create_ticket_type(validated_data) -> TicketType:
        event = validated_data.get('event')
        if event.event_status != 'PUBLISHED':
            raise ValidationError("Cannot create ticket type for unpublished event.")
        return TicketType.objects.create(**validated_data)

    @staticmethod
    def update_ticket_type(ticket_type: TicketType, validated_data) -> TicketType:
        for key, value in validated_data.items():
            setattr(ticket_type, key, value)
        ticket_type.save()
        return ticket_type

    @staticmethod
    def delete_ticket_type(ticket_type: TicketType) -> None:
        ticket_type.delete()

    @staticmethod
    def reserve_ticket(ticket_type: TicketType):
        with transaction.atomic():
            ticket_type.refresh_from_db()
            if ticket_type.quantity_available <= 0:
                raise ValidationError('No tickets available for this type.')
            ticket_type.quantity_available -= 1
            ticket_type.save()

    @staticmethod
    def release_ticket(ticket_type: TicketType):
        with transaction.atomic():
            ticket_type.refresh_from_db()
            ticket_type.quantity_available += 1
            ticket_type.save()