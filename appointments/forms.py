import datetime
from django import forms
from django.utils import timezone
from .models import Appointment, Prescription
from accounts.models import User, DoctorProfile


class BookAppointmentForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.DOCTOR, doctor_profile__is_available=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select Specialist / Doctor"
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()
        })
    )
    appointment_time = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'}),
        choices=[
            ('09:00', '09:00 AM'),
            ('09:30', '09:30 AM'),
            ('10:00', '10:00 AM'),
            ('10:30', '10:30 AM'),
            ('11:00', '11:00 AM'),
            ('11:30', '11:30 AM'),
            ('12:00', '12:00 PM'),
            ('14:00', '02:00 PM'),
            ('14:30', '02:30 PM'),
            ('15:00', '03:00 PM'),
            ('15:30', '03:30 PM'),
            ('16:00', '04:00 PM'),
            ('16:30', '04:30 PM'),
        ]
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'symptoms']
        widgets = {
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your symptoms, main concerns, or duration of issue...'
            }),
        }

    def clean_appointment_date(self):
        appt_date = self.cleaned_data.get('appointment_date')
        if appt_date and appt_date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return appt_date


class AppointmentStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'doctor_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'doctor_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Clinical observations & recommendations'}),
        }


class PrescriptionForm(forms.ModelForm):
    follow_up_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Prescription
        fields = ['diagnosis', 'medicines', 'instructions', 'follow_up_date']
        widgets = {
            'diagnosis': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Type 2 Diabetes Mellitus with Mild Hypertension'
            }),
            'medicines': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '1. Metformin 500mg - 1 tablet twice daily after meals\n2. Telmisartan 40mg - 1 tablet once daily in morning'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lifestyle and dietary restrictions (e.g. Low sodium diet, 30 min daily brisk walk)'
            }),
        }
