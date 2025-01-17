from datetime import timezone
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

class TicketStatusChoices(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'INACTIVE'
    PENDING_PAYMENT = 'PENDING_PAYMENT ', 'Pending_Payment'
    CANCELED = 'CANCELED', 'Canceled'
    USED = 'USED', 'Used'
    EXPIRED = 'EXPIRED', 'Expired'
    

class TicketType(models.Model):
    event = models.ForeignKey(Event, related_name='ticket_types', on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=50, choices=TicketTypeNameChoices.choices, default=TicketTypeNameChoices.REGULAR, null=False, blank=False)
    description =models.TextField(null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    quantity_available = models.IntegerField(null=False, blank=False)
    sale_start = models.DateTimeField(null=False, blank=False)
    sale_end = models.DateTimeField(null=False, blank=False)
    ticket_type_status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, null=False, blank=False)

    def reserve_ticket(self):
        with transaction.atomic():
            self.refresh_from_db()  
            if self.quantity_available <= 0:
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
        if self.quantity_available < 1:
            raise ValidationError('The total capacity must be greater than zero.')
        if self.event.event_status != 'PUBLISHED':
            raise ValidationError('Tickets can only be created for published events.')
        if self.name == TicketTypeNameChoices.SOCIAL and self.price > 0:
            raise ValidationError('The social ticket must be free.')
        
    def save(self, *args, **kwargs):
        self.clean()
        return super(TicketType, self).save(*args, **kwargs)

class Ticket(models.Model):
    ticket_type = models.ForeignKey(TicketType, related_name='tickets', on_delete=models.CASCADE, null=False, blank=False)
    buyer = models.ForeignKey(User, related_name='tickets', on_delete=models.CASCADE, null=False, blank=False)
    unique_code = models.CharField(max_length=50, default=generate_unique_code, unique=True, null=False, blank=False, editable=False)
    ticket_status = models.CharField(max_length=50, choices=TicketStatusChoices.choices, default=TicketStatusChoices.PENDING_PAYMENT, null=False, blank=False)
    bought_at = models.DateTimeField(null=False, blank=False)
    used_at = models.DateTimeField(null=True, blank=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    def clean(self):
        if self.bought_at > self.used_at:
            raise ValidationError('The bought date must be before the used date')       
        if self.price_paid < 0:
            raise ValidationError('The price paid must be greater than zero')

    def save(self, *args, **kwargs):
        self.clean()
        return super(Ticket, self).save(*args, **kwargs)

    def change_ticket_status(self, new_status):
        valid_statuses = {'ACTIVE', 'INACTIVE', 'PENDING_PAYMENT', 'CANCELED', 'USED', 'EXPIRED'}
        
        if new_status not in valid_statuses:
            raise ValidationError(f"'{new_status}' is not a valid ticket status.")
        
        if self.ticket_status == 'CANCELED' or self.ticket_status == 'USED':
            raise ValidationError(f"Ticket cannot transition from '{self.ticket_status}' to '{new_status}'.")
        
        if new_status == 'USED' and self.ticket_status != 'ACTIVE':
            raise ValidationError(f"Only ACTIVE tickets can be marked as USED.")
        
        if new_status == 'ACTIVE' and self.ticket_status != 'PENDING_PAYMENT':
            raise ValidationError(f"Only PENDING_PAYMENT tickets can transition to ACTIVE.")

        self.ticket_status = new_status
        if new_status == 'USED':
            self.used_at = timezone.now()
        self.save()

    def generate_qr_response(self):     
        qr_data = {
            'ticket_code': self.unique_code,
            'event': self.ticket_type.event.title,
            'buyer': self.buyer.name,
            'ticket_type': self.ticket_type.name,
            'ticket_status': self.ticket_status,
        }

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )

        qr.add_data(str(qr_data))
        qr.make(fit=True)

        img = qr.make_image(fill_color='black', back_color='white')
        response = HttpResponse(content_type='image/png')
        img.save(response, 'PNG')
        
        return response    
        
        