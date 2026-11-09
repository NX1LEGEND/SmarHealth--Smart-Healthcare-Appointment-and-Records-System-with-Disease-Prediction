import logging
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import Notification, Appointment

logger = logging.getLogger(__name__)


def send_appointment_notification(appointment, event_type='BOOKED'):
    """
    Sends email, SMS, and in-app notifications for appointment lifecycle events.
    event_type: 'BOOKED', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'REMINDER'
    """
    patient = appointment.patient
    doctor = appointment.doctor
    appt_date = appointment.appointment_date.strftime('%B %d, %Y')
    appt_time = appointment.appointment_time.strftime('%I:%M %p')
    
    # 1. Compose notifications
    if event_type == 'BOOKED':
        # Patient Notification
        p_title = "Appointment Request Received"
        p_msg = f"Your appointment request with {doctor.get_full_name_or_username()} on {appt_date} at {appt_time} has been received and is pending confirmation."
        Notification.objects.create(
            recipient=patient,
            title=p_title,
            message=p_msg,
            notification_type=Notification.NotificationType.BOOKING,
            link=f"/appointments/{appointment.id}/"
        )
        # Doctor Notification
        d_title = "New Appointment Booking Request"
        d_msg = f"Patient {patient.get_full_name_or_username()} has requested an appointment on {appt_date} at {appt_time}."
        Notification.objects.create(
            recipient=doctor,
            title=d_title,
            message=d_msg,
            notification_type=Notification.NotificationType.BOOKING,
            link=f"/appointments/{appointment.id}/"
        )
        send_email_notification(patient.email, p_title, p_msg)
        send_sms_notification(patient.phone_number, f"SmartHealth: {p_msg}")
        
    elif event_type == 'CONFIRMED':
        p_title = "Appointment Confirmed!"
        p_msg = f"Great news! Dr. {doctor.get_full_name()} confirmed your appointment on {appt_date} at {appt_time}."
        Notification.objects.create(
            recipient=patient,
            title=p_title,
            message=p_msg,
            notification_type=Notification.NotificationType.CONFIRMATION,
            link=f"/appointments/{appointment.id}/"
        )
        send_email_notification(patient.email, p_title, p_msg)
        send_sms_notification(patient.phone_number, f"SmartHealth: {p_msg}")
        
    elif event_type == 'CANCELLED':
        p_title = "Appointment Cancelled"
        p_msg = f"Your appointment with {doctor.get_full_name_or_username()} on {appt_date} at {appt_time} has been cancelled."
        Notification.objects.create(
            recipient=patient,
            title=p_title,
            message=p_msg,
            notification_type=Notification.NotificationType.CANCELLATION,
            link=f"/appointments/{appointment.id}/"
        )
        d_title = "Appointment Cancelled"
        d_msg = f"Appointment with {patient.get_full_name_or_username()} on {appt_date} at {appt_time} was cancelled."
        Notification.objects.create(
            recipient=doctor,
            title=d_title,
            message=d_msg,
            notification_type=Notification.NotificationType.CANCELLATION,
            link=f"/appointments/{appointment.id}/"
        )
        send_email_notification(patient.email, p_title, p_msg)
        send_sms_notification(patient.phone_number, f"SmartHealth: {p_msg}")
        
    elif event_type == 'REMINDER':
        p_title = "Upcoming Appointment Reminder"
        p_msg = f"Friendly reminder: You have an appointment with {doctor.get_full_name_or_username()} tomorrow on {appt_date} at {appt_time}. Please bring your previous test records."
        Notification.objects.create(
            recipient=patient,
            title=p_title,
            message=p_msg,
            notification_type=Notification.NotificationType.REMINDER,
            link=f"/appointments/{appointment.id}/"
        )
        send_email_notification(patient.email, p_title, p_msg)
        send_sms_notification(patient.phone_number, f"SmartHealth Reminder: {p_msg}")
        appointment.reminder_sent = True
        appointment.save(update_fields=['reminder_sent'])


def send_email_notification(to_email, subject, body):
    """Sends email via configured Django Email Backend"""
    if not to_email:
        return False
    try:
        send_mail(
            subject=f"[Smart Healthcare] {subject}",
            message=body,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@smarthealth.local'),
            recipient_list=[to_email],
            fail_silently=True
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_sms_notification(phone_number, message_text):
    """
    Sends SMS reminder via Twilio API if credentials are provided,
    otherwise records simulated SMS dispatch in system logs.
    """
    if not phone_number:
        return False
        
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '')
    
    if account_sid and auth_token and from_number:
        try:
            # Twilio integration
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            client.messages.create(
                body=message_text,
                from_=from_number,
                to=phone_number
            )
            logger.info(f"Twilio SMS dispatched to {phone_number}")
            return True
        except Exception as e:
            logger.warning(f"Twilio dispatch failed ({e}), falling back to simulated SMS logger.")
            
    # Simulated SMS Logger (Dev & Demo mode)
    print("\n" + "=" * 55)
    print(f"📱 [SMS GATEWAY DISPATCH SIMULATOR]")
    print(f"To:      {phone_number}")
    print(f"Time:    {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Message: {message_text}")
    print("=" * 55 + "\n")
    return True
