import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from accounts.models import User, DoctorProfile, PatientProfile
from accounts.decorators import patient_required, doctor_required, admin_required
from appointments.models import Appointment, Prescription, Notification
from records.models import MedicalRecord
from prediction.models import HealthPrediction


def home_view(request):
    featured_doctors = User.objects.filter(
        role=User.Role.DOCTOR,
        doctor_profile__is_available=True
    ).select_related('doctor_profile')[:4]
    
    specialties_count = DoctorProfile.objects.values('specialty').distinct().count()
    doctors_count = User.objects.filter(role=User.Role.DOCTOR).count()
    patients_count = User.objects.filter(role=User.Role.PATIENT).count()
    
    return render(request, 'core/home.html', {
        'featured_doctors': featured_doctors,
        'specialties_count': specialties_count or 6,
        'doctors_count': doctors_count or 12,
        'patients_count': patients_count or 50,
    })


@login_required
def dashboard_redirect_view(request):
    user = request.user
    if user.is_hospital_admin:
        return redirect('core:admin_dashboard')
    elif user.is_doctor:
        return redirect('core:doctor_dashboard')
    elif user.is_patient:
        return redirect('core:patient_dashboard')
    return redirect('core:home')


@login_required
@patient_required
def patient_dashboard_view(request):
    user = request.user
    today = timezone.now().date()
    
    # Appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=user,
        appointment_date__gte=today,
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
    ).select_related('doctor', 'doctor__doctor_profile').order_by('appointment_date', 'appointment_time')[:5]
    
    recent_appointments = Appointment.objects.filter(
        patient=user
    ).select_related('doctor', 'doctor__doctor_profile').order_by('-appointment_date', '-appointment_time')[:5]
    
    # Medical records
    recent_records = MedicalRecord.objects.filter(patient=user).order_by('-record_date')[:5]
    
    # Health predictions
    recent_predictions = HealthPrediction.objects.filter(patient=user).order_by('-created_at')[:4]
    
    # Stats
    total_appointments = Appointment.objects.filter(patient=user).count()
    total_records = MedicalRecord.objects.filter(patient=user).count()
    total_predictions = HealthPrediction.objects.filter(patient=user).count()
    
    return render(request, 'core/patient_dashboard.html', {
        'upcoming_appointments': upcoming_appointments,
        'recent_appointments': recent_appointments,
        'recent_records': recent_records,
        'recent_predictions': recent_predictions,
        'total_appointments': total_appointments,
        'total_records': total_records,
        'total_predictions': total_predictions,
    })


@login_required
@doctor_required
def doctor_dashboard_view(request):
    user = request.user
    today = timezone.now().date()
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(
        doctor=user,
        appointment_date=today
    ).select_related('patient').order_by('appointment_time')
    
    # Pending requests requiring doctor confirmation
    pending_appointments = Appointment.objects.filter(
        doctor=user,
        status=Appointment.Status.PENDING
    ).select_related('patient').order_by('appointment_date', 'appointment_time')
    
    # Upcoming confirmed appointments
    upcoming_appointments = Appointment.objects.filter(
        doctor=user,
        appointment_date__gt=today,
        status=Appointment.Status.CONFIRMED
    ).select_related('patient').order_by('appointment_date', 'appointment_time')[:8]
    
    # Stats
    total_patients = Appointment.objects.filter(doctor=user).values('patient').distinct().count()
    total_consultations = Appointment.objects.filter(doctor=user, status=Appointment.Status.COMPLETED).count()
    prescriptions_issued = Prescription.objects.filter(doctor=user).count()
    
    return render(request, 'core/doctor_dashboard.html', {
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'upcoming_appointments': upcoming_appointments,
        'total_patients': total_patients,
        'total_consultations': total_consultations,
        'prescriptions_issued': prescriptions_issued,
        'today': today,
    })


@login_required
@admin_required
def admin_dashboard_view(request):
    today = timezone.now().date()
    
    # Counts
    total_patients = User.objects.filter(role=User.Role.PATIENT).count()
    total_doctors = User.objects.filter(role=User.Role.DOCTOR).count()
    total_appointments = Appointment.objects.count()
    total_records = MedicalRecord.objects.count()
    total_predictions = HealthPrediction.objects.count()
    
    # Status Breakdown
    status_counts = {
        'pending': Appointment.objects.filter(status=Appointment.Status.PENDING).count(),
        'confirmed': Appointment.objects.filter(status=Appointment.Status.CONFIRMED).count(),
        'completed': Appointment.objects.filter(status=Appointment.Status.COMPLETED).count(),
        'cancelled': Appointment.objects.filter(status=Appointment.Status.CANCELLED).count(),
    }
    
    # Prediction Risk Breakdown
    diabetes_high = HealthPrediction.objects.filter(disease_type=HealthPrediction.Disease.DIABETES, risk_level='HIGH').count()
    diabetes_mod = HealthPrediction.objects.filter(disease_type=HealthPrediction.Disease.DIABETES, risk_level='MODERATE').count()
    diabetes_low = HealthPrediction.objects.filter(disease_type=HealthPrediction.Disease.DIABETES, risk_level='LOW').count()
    
    heart_high = HealthPrediction.objects.filter(disease_type=HealthPrediction.Disease.HEART_DISEASE, risk_level='HIGH').count()
    heart_mod = HealthPrediction.objects.filter(disease_type=HealthPrediction.Disease.HEART_DISEASE, risk_level='MODERATE').count()
    heart_low = HealthPrediction.objects.filter(disease_type=HealthPrediction.Disease.HEART_DISEASE, risk_level='LOW').count()
    
    # Recent appointments
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:10]
    
    # Doctor list
    doctors = User.objects.filter(role=User.Role.DOCTOR).select_related('doctor_profile')
    
    return render(request, 'core/admin_dashboard.html', {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'total_records': total_records,
        'total_predictions': total_predictions,
        'status_counts': status_counts,
        'diabetes_stats': {'high': diabetes_high, 'mod': diabetes_mod, 'low': diabetes_low},
        'heart_stats': {'high': heart_high, 'mod': heart_mod, 'low': heart_low},
        'recent_appointments': recent_appointments,
        'doctors': doctors,
    })
