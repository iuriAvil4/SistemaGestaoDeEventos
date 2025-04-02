from tickets.tasks import send_custom_email

def send_qrcode_email(user_email, event, qr_code_buffer):
    subject = "Ticket QR Code"
    message = f"Your ticket QR Code for {event} is attached."
    attachments = [("ticket_qr.png", qr_code_buffer.getvalue(), "image/png")]
    send_custom_email.delay(subject, message, [user_email], attachments=attachments)

def send_reservation_confirmation_email(user_email, unique_code, price_paid):
    subject = "Reservation Confirmed"
    message = f"Your reservation has been confirmed!\nTicket code: {unique_code}\nPrice paid: {price_paid}"
    send_custom_email.delay(subject, message, [user_email])