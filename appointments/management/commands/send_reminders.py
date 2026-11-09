import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from appointments.models import Appointment
from appointments.reminders import send_appointment_notification


class Command(BaseCommand):
    help = 'Scans for confirmed appointments happening within the next 24-48 hours and sends email/SMS reminders.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        target_dates = [today, today + datetime.timedelta(days=1)]
        
        appointments = Appointment.objects.filter(
            appointment_date__in=target_dates,
            status=Appointment.Status.CONFIRMED,
            reminder_sent=False
        )
        
        count = appointments.count()
        self.stdout.write(f"Found {count} upcoming confirmed appointments requiring reminders.")
        
        sent_count = 0
        for appt in appointments:
            send_appointment_notification(appt, event_type='REMINDER')
            sent_count += 1
            self.stdout.write(self.style.SUCCESS(
                f"Sent reminder for appointment #{appt.id} (Patient: {appt.patient.username}, Doctor: {appt.doctor.username}, Date: {appt.appointment_date})"
            ))
            
        self.stdout.write(self.style.SUCCESS(f"Successfully processed and dispatched {sent_count} reminders."))
