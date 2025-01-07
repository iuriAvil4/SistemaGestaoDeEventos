from django.db import models
from django.http import HttpResponse
from events.models import Event
from users.models import User
from io import BytesIO
import uuid 
import qrcode


def generate_unique_code():
    return f'TIX-{uuid.uuid4().hex[:8].upper()}'

class TicketTypeName(models.TextChoices):
    MEIA_ENTRADA = 'MEIA_ENTRADA', 'Meia Entrada'
    INTEIRA = 'INTEIRA', 'Inteira'
    SOCIAL = 'SOCIAL', 'Social'
    REGULAR = 'REGULAR', 'Regular'
    VIP = 'VIP', 'VIP'
    CAMAROTE = 'CAMAROTE', 'Camarote'

class Status(models.TextChoices):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'

class TicketType(models.Model):
    event = models.ForeignKey(Event, related_name='ticket_types', on_delete=models.CASCADE, null=False, blank=False)
    name = models.ChairField(max_lenght=20, choices=TicketTypeName.choices, default=TicketTypeName.REGULAR, null=False, blank=False)
    description =models.TextField(null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, localize=True, null=False, blank=False)
    quantity_avaiable = models.IntegerField(null=False, blank=False)
    sale_start = models.DateTimeField(null=False, blank=False)
    sale_end = models.DateTimeField(null=False, blank=False)
    status = models.CharField(max_lenght=20, choices=Status.choices, default=Status.ACTIVE, null=False, blank=False)

class Ticket(models.Model):
    ticket_type = models.ForeignKey(TicketType, related_name='tickets', on_delete=models.CASCADE, null=False, blank=False)
    buyer = models.ForeignKey(User, related_name='tickets', on_delete=models.CASCADE, null=False, blank=False)
    unique_code = models.CharField(max_lenght=20, default=generate_unique_code, unique=True, null=False, blank=False, editable=False)
    status = models.CharField(max_lenght=20, choices=Status.choices, default=Status.ACTIVE, null=False, blank=False)
    bought_at = models.DateTimeField(null=False, blank=False)
    used_at = models.DateTimeField(null=True, blank=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, localize=True, null=False, blank=False)

    def generate_qr_response(self):     
        qr_data = {
            'ticket_code': self.unique_code,
            'event': self.ticket_type.event.title,
            'buyer': self.buyer.name,
            'ticket_type': self.ticket_type.name,
            'status': self.status,
        }

        qr = qrcode.QRCode(
            version=1,
            error_connection=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(str(qr_data))
        qr.make(fit=True)

        img = qr.make_image(fill_color='black', back_color='white')
        response = HttpResponse(content_type='image/png')
        img.save(response, 'PNG')
        
        return response    
        
        