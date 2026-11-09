from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        DOCTOR = 'DOCTOR', 'Doctor'
        ADMIN = 'ADMIN', 'Hospital Admin'

    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ]

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=2, choices=Gender.choices, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_hospital_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def get_full_name_or_username(self):
        name = self.get_full_name()
        if name:
            if self.is_doctor and not name.lower().startswith('dr.'):
                return f"Dr. {name}"
            return name
        return self.username

    def __str__(self):
        return f"{self.get_full_name_or_username()} ({self.get_role_display()})"


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialty = models.CharField(max_length=100, help_text="e.g. Cardiology, Endocrinology, General Medicine")
    license_number = models.CharField(max_length=50)
    qualification = models.CharField(max_length=150, help_text="e.g. MBBS, MD (Medicine), DM (Cardiology)")
    experience_years = models.PositiveIntegerField(default=1)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=500.00)
    bio = models.TextField(blank=True)
    clinic_address = models.CharField(max_length=255, blank=True)
    available_days = models.CharField(max_length=200, default='Monday, Tuesday, Wednesday, Thursday, Friday')
    start_time = models.TimeField(default='09:00')
    end_time = models.TimeField(default='17:00')
    slot_duration_minutes = models.PositiveIntegerField(default=30)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialty}"


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    allergies = models.TextField(blank=True, help_text="Known drug or food allergies")
    chronic_conditions = models.TextField(blank=True, help_text="e.g. Hypertension, Asthma")
    current_medications = models.TextField(blank=True)

    def __str__(self):
        return f"Patient Profile: {self.user.get_full_name() or self.user.username}"
