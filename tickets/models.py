from django.utils import timezone
from django.db import models
from django.forms import ValidationError
from django.http import HttpResponse
from django.db import transaction
from events.models import Event
from users.models import User
from io import BytesIO
import uuid 
import qrcode


def generate_unique_code():
    return f'TIX-{uuid.uuid4().hex[:8].upper()}'

class TicketType(models.Model):
    class TicketTypeNameChoices(models.TextChoices):
        MEIA_ENTRADA = 'MEIA_ENTRADA', 'Meia Entrada'
        INTEIRA = 'INTEIRA', 'Inteira'
        SOCIAL = 'SOCIAL', 'Social'
        REGULAR = 'REGULAR', 'Regular'
        VIP = 'VIP', 'VIP'
        CAMAROTE = 'CAMAROTE', 'Camarote'

    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE'
        INACTIVE = 'INACTIVE'

    event = models.ForeignKey(Event, related_name='ticket_types', on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=50, choices=TicketTypeNameChoices.choices, default=TicketTypeNameChoices.REGULAR, null=False, blank=False)
    description =models.TextField(null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    quantity_available = models.IntegerField(null=False, blank=False)
    sale_start = models.DateTimeField(null=False, blank=False)
    sale_end = models.DateTimeField(null=False, blank=False)
    ticket_type_status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, null=False, blank=False)


    class Meta:
        db_table = 'ticket_types'

    def reserve_ticket(self):
        with transaction.atomic():
            self.refresh_from_db()  
            if self.quantity_available == 0:
                raise ValidationError('No tickets available for this type.')
            self.quantity_available -= 1
            self.save()

    def release_ticket(self):
        with transaction.atomic():
            self.refresh_from_db()
            self.quantity_available += 1
            self.save()


    def clean(self):
        if self.sale_start > self.sale_end:
            raise ValidationError('The start date must be before the end date.')       
        if self.quantity_available < 0:
            raise ValidationError('The total capacity must be greater than zero.')
        if self.event.event_status != 'PUBLISHED':
            raise ValidationError('Tickets can only be created for published events.')
        if self.name == TicketType.TicketTypeNameChoices.SOCIAL and self.price > 0:
            raise ValidationError('The social ticket must be free.')
        
    def save(self, *args, **kwargs):
        self.clean()
        return super(TicketType, self).save(*args, **kwargs)


class Ticket(models.Model):
    class TicketStatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'INACTIVE'
        PENDING_PAYMENT = 'PENDING_PAYMENT', 'Pending_Payment'
        CANCELED = 'CANCELED', 'Canceled'
        USED = 'USED', 'Used'
        EXPIRED = 'EXPIRED', 'Expired'

    ticket_type = models.ForeignKey(TicketType, related_name='tickets', on_delete=models.CASCADE, null=False, blank=False)
    buyer = models.ForeignKey(User, related_name='tickets', on_delete=models.CASCADE, null=False, blank=False)
    unique_code = models.CharField(max_length=50, default=generate_unique_code, unique=True, null=False, blank=False, editable=False)
    ticket_status = models.CharField(max_length=50, choices=TicketStatusChoices.choices, default=TicketStatusChoices.PENDING_PAYMENT, null=False, blank=False)
    bought_at = models.DateTimeField(null=False, blank=False)
    used_at = models.DateTimeField(null=True, blank=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    class Meta:
        db_table = 'tickets'

    def clean(self):
        if self.bought_at > self.used_at:
            raise ValidationError('The bought date must be before the used date')       
        if self.price_paid < 0:
            raise ValidationError('The price paid must be greater than zero')

    def save(self, *args, **kwargs):
        self.clean()
        return super(Ticket, self).save(*args, **kwargs)

    def generate_qr_code(ticket):
        qr_data = f"Ticket: {ticket.unique_code}\nEvent: {ticket.ticket_type.event.title}\nBuyer: {ticket.buyer.name}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer  
        