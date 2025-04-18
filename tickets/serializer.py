from django.forms import ValidationError
from rest_framework import serializers
from .models import Ticket, TicketType


class TicketRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_type', 'buyer', 'unique_code', 'ticket_status', 'bought_at', 'used_at', 'price_paid'
        ]

    def validate(self, data):
        ticket_type = data.get('ticket_type')
        buyer = data.get('buyer')

        """ if Ticket.objects.filter(ticket_type=ticket_type, buyer=buyer).exists():
            raise serializers.ValidationError("O usuário já possui um ticket deste tipo para este evento.") """

        if data['bought_at'] > data['used_at']:
            raise serializers.ValidationError("The bought date must be before the used date.")
        if data['price_paid'] < 0:
            raise serializers.ValidationError("The price paid must be greater than zero.")
        return data
    

class TicketTypeRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = [
            'id', 'event', 'name', 'description', 'price', 'quantity_available', 'sale_start', 'sale_end', 'ticket_type_status'
        ]

    def validate(self, data):
        if data['sale_start'] > data['sale_end']:
            raise serializers.ValidationError("The sale start date must be before the sale end date.")
        if data['quantity_available'] < 0:
            raise serializers.ValidationError("The quantity available must be greater than zero.")
        return data


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_type', 'buyer', 'unique_code', 'ticket_status', 'bought_at', 'used_at', 'price_paid'
        ]


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = [
            'id', 'event', 'name', 'description', 'price', 'quantity_available', 'sale_start', 'sale_end', 'ticket_type_status'
        ]