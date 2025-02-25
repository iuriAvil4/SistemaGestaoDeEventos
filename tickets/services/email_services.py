from tasks import send_custom_email

def send_payment_confirmation_email(user_email, order_id):
    subject = "Payment Confirmation"
    message = f"Your payment for order {order_id} has been confirmed successfully."
    send_custom_email.delay(subject, message, [user_email])

def send_reservation_confirmation_email(user_email, reservation_details):
    subject = "Reservation Confirmed"
    message = f"Your reservation has been confirmed! Details: {reservation_details}"
    send_custom_email.delay(subject, message, [user_email])