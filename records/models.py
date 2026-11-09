from django.db import models
from django.conf import settings
import os


class MedicalRecord(models.Model):
    class RecordType(models.TextChoices):
        LAB_REPORT = 'LAB_REPORT', 'Blood / Lab Test Report'
        IMAGING = 'IMAGING', 'X-Ray / MRI / CT / Ultrasound Scan'
        ECG_ECHO = 'ECG_ECHO', 'ECG / Echo Cardiogram'
        DISCHARGE = 'DISCHARGE', 'Discharge Summary'
        PRESCRIPTION = 'PRESCRIPTION', 'Prescription Slip'
        OTHER = 'OTHER', 'Other Medical Document'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_records',
        limit_choices_to={'role': 'PATIENT'}
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_records'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='records'
    )
    title = models.CharField(max_length=200, help_text="e.g. Fasting Blood Sugar Test, Lipid Profile")
    record_type = models.CharField(
        max_length=30,
        choices=RecordType.choices,
        default=RecordType.LAB_REPORT
    )
    record_date = models.DateField(help_text="Date when test/procedure was conducted")
    file = models.FileField(upload_to='secure_records/%Y/%m/')
    notes = models.TextField(blank=True, help_text="Findings, observations, or physician notes")
    file_size_bytes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-record_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.patient.get_full_name() or self.patient.username} ({self.record_date})"

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, 'size'):
            self.file_size_bytes = self.file.size
        super().save(*args, **kwargs)

    @property
    def file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''

    @property
    def is_image(self):
        return self.file_extension in ['.jpg', '.jpeg', '.png', '.webp']

    @property
    def is_pdf(self):
        return self.file_extension == '.pdf'

    @property
    def file_size_display(self):
        if not self.file_size_bytes:
            return "0 KB"
        kb = self.file_size_bytes / 1024
        if kb < 1024:
            return f"{kb:.1f} KB"
        mb = kb / 1024
        return f"{mb:.2f} MB"
