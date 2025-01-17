import qrcode
import base64
from io import BytesIO
from django.core.mail import EmailMessage
from celery import shared_task
from django.template.loader import render_to_string
from apps.booking.models import Appointment
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_booking_confirmation_email(appointment_id):
    # Get the appointment instance
    logger.info(f"Sending confirmation for appointment {appointment_id}")
    appointment = Appointment.objects.get(id=appointment_id)

    # Generate QR code
    qr_data = f"{appointment.id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code to BytesIO object
    qr_buffer = BytesIO()
    img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # Create and send email with CID
    email = EmailMessage(
        subject=f"Booking Confirmation - {appointment.service.name}",
        body=None,  # We'll use an HTML template
        from_email=settings.EMAIL_HOST_USER,
        to=[appointment.customer.email],
    )

    # Attach QR code image and set Content ID
    qr_code_filename = f"QR_code_{appointment.id}.png"
    email.attach(qr_code_filename, qr_buffer.getvalue(), "image/png")
    qr_code_cid = f"cid:{qr_code_filename}"

    # Render email template
    email_content = render_to_string(
        "emails/booking_confirmation.html",
        {
            "appointment": appointment,
            "qr_code_cid": qr_code_cid,  
        }
    )
    email.body = email_content
    email.content_subtype = "html"
    email.send()

  
    qr_buffer.close()
