import os
from django import forms
from django.utils import timezone
from .models import MedicalRecord
from appointments.models import Appointment

ALLOWED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg', '.webp']
MAX_FILE_SIZE_MB = 10


class MedicalRecordUploadForm(forms.ModelForm):
    record_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'max': timezone.now().date().isoformat()}),
        initial=timezone.now().date
    )

    class Meta:
        model = MedicalRecord
        fields = ['title', 'record_type', 'record_date', 'appointment', 'file', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Fasting Blood Sugar Lab Report'}),
            'record_type': forms.Select(attrs={'class': 'form-select'}),
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Diagnostic summary, key values, or test results...'}),
        }

    def __init__(self, *args, **kwargs):
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        if patient:
            self.fields['appointment'].queryset = Appointment.objects.filter(patient=patient)
            self.fields['appointment'].required = False
            self.fields['appointment'].empty_label = "None (Independent Upload)"

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if uploaded_file:
            # Validate File Extension
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            # Validate File Size
            if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(f"File size exceeds maximum allowable limit of {MAX_FILE_SIZE_MB}MB.")
        return uploaded_file
