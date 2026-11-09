from django.db import models
from django.conf import settings


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 'PATIENT'}
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'DOCTOR'}
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    symptoms = models.TextField(help_text="Describe patient symptoms or reason for visit")
    doctor_notes = models.TextField(blank=True, help_text="Clinical observations or consultation notes")
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        return f"{self.patient.get_full_name() or self.patient.username} with {self.doctor.get_full_name_or_username()} on {self.appointment_date} at {self.appointment_time}"

    @property
    def is_upcoming(self):
        import datetime
        from django.utils import timezone
        now = timezone.now()
        appt_dt = datetime.datetime.combine(self.appointment_date, self.appointment_time)
        return appt_dt >= now.replace(tzinfo=None) and self.status in [self.Status.PENDING, self.Status.CONFIRMED]


class Prescription(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='prescription'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions_written'
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions_received'
    )
    diagnosis = models.TextField(help_text="Clinical diagnosis")
    medicines = models.TextField(help_text="List medicines, dosage, timing (e.g., Paracetamol 500mg - 1-0-1 after food)")
    instructions = models.TextField(blank=True, help_text="Dietary, physical, or lifestyle precautions")
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.get_full_name() or self.patient.username} by {self.doctor.get_full_name_or_username()} ({self.created_at.strftime('%Y-%m-%d')})"


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        BOOKING = 'BOOKING', 'Appointment Booked'
        CONFIRMATION = 'CONFIRMATION', 'Appointment Confirmed'
        CANCELLATION = 'CANCELLATION', 'Appointment Cancelled'
        COMPLETION = 'COMPLETION', 'Appointment Completed'
        REMINDER = 'REMINDER', 'Appointment Reminder'
        REPORT = 'REPORT', 'Medical Report Uploaded'
        PREDICTION = 'PREDICTION', 'Health Risk Alert'
        GENERAL = 'GENERAL', 'System Notice'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL
    )
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
