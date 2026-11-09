from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import Appointment, Prescription, Notification
from .forms import BookAppointmentForm, AppointmentStatusUpdateForm, PrescriptionForm
from accounts.models import User, DoctorProfile
from accounts.decorators import patient_required, doctor_required
from .reminders import send_appointment_notification


def doctor_directory_view(request):
    query = request.GET.get('q', '').strip()
    specialty_filter = request.GET.get('specialty', '').strip()
    
    doctors = User.objects.filter(role=User.Role.DOCTOR, doctor_profile__is_available=True).select_related('doctor_profile')
    
    if query:
        doctors = doctors.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(doctor_profile__specialty__icontains=query) |
            Q(doctor_profile__qualification__icontains=query)
        )
        
    if specialty_filter:
        doctors = doctors.filter(doctor_profile__specialty__iexact=specialty_filter)
        
    # Get distinct specialties for filter chips
    specialties = DoctorProfile.objects.values_list('specialty', flat=True).distinct()
    
    return render(request, 'appointments/doctor_directory.html', {
        'doctors': doctors,
        'query': query,
        'specialty_filter': specialty_filter,
        'specialties': sorted(list(set(specialties))),
    })


def doctor_detail_view(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id, role=User.Role.DOCTOR)
    return render(request, 'appointments/doctor_detail.html', {
        'doctor': doctor,
        'profile': doctor.doctor_profile,
    })


@login_required
@patient_required
def book_appointment_view(request):
    doctor_id = request.GET.get('doctor')
    initial_data = {}
    if doctor_id:
        try:
            initial_data['doctor'] = User.objects.get(id=doctor_id, role=User.Role.DOCTOR)
        except User.DoesNotExist:
            pass
            
    if request.method == 'POST':
        form = BookAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.status = Appointment.Status.PENDING
            appointment.save()
            
            # Send Notification & Reminders
            send_appointment_notification(appointment, event_type='BOOKED')
            
            messages.success(request, f"Appointment request submitted successfully with Dr. {appointment.doctor.get_full_name()}!")
            return redirect('appointments:detail', appointment_id=appointment.id)
        else:
            messages.error(request, "Please fix the errors in the booking form.")
    else:
        form = BookAppointmentForm(initial=initial_data)
        
    return render(request, 'appointments/book_appointment.html', {'form': form})


@login_required
def appointment_detail_view(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'doctor', 'doctor__doctor_profile'),
        id=appointment_id
    )
    
    # Secure Access Check
    user = request.user
    if not (user.is_hospital_admin or appointment.patient == user or appointment.doctor == user):
        raise PermissionDenied("You are not authorized to view this appointment.")
        
    # Check for prescription
    prescription = getattr(appointment, 'prescription', None)
    
    # Associated records
    records = appointment.records.all()
    
    # Prescription Form for Doctor
    prescription_form = None
    status_form = None
    if user == appointment.doctor or user.is_hospital_admin:
        status_form = AppointmentStatusUpdateForm(instance=appointment)
        if not prescription:
            prescription_form = PrescriptionForm()
            
    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'prescription': prescription,
        'records': records,
        'status_form': status_form,
        'prescription_form': prescription_form,
    })


@login_required
def update_appointment_status_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user
    
    if not (user == appointment.doctor or user.is_hospital_admin):
        raise PermissionDenied("Only the consulting doctor or administrator can modify appointment status.")
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('doctor_notes', '')
        
        if new_status in dict(Appointment.Status.choices):
            old_status = appointment.status
            appointment.status = new_status
            if notes:
                appointment.doctor_notes = notes
            appointment.save()
            
            # Notify on status changes
            if new_status == Appointment.Status.CONFIRMED and old_status != Appointment.Status.CONFIRMED:
                send_appointment_notification(appointment, event_type='CONFIRMED')
            elif new_status == Appointment.Status.CANCELLED and old_status != Appointment.Status.CANCELLED:
                send_appointment_notification(appointment, event_type='CANCELLED')
            elif new_status == Appointment.Status.COMPLETED:
                Notification.objects.create(
                    recipient=appointment.patient,
                    title="Appointment Completed",
                    message=f"Your consultation with Dr. {appointment.doctor.get_full_name()} is marked completed. You can view doctor notes and prescriptions in your records.",
                    notification_type=Notification.NotificationType.COMPLETION,
                    link=f"/appointments/{appointment.id}/"
                )
                
            messages.success(request, f"Appointment status updated to '{appointment.get_status_display()}'.")
            
    return redirect('appointments:detail', appointment_id=appointment.id)


@login_required
@doctor_required
def create_prescription_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.doctor != request.user and not request.user.is_hospital_admin:
        raise PermissionDenied("Only the attending doctor can write this prescription.")
        
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.doctor = request.user
            prescription.patient = appointment.patient
            prescription.save()
            
            # Automatically set status to COMPLETED if not already
            if appointment.status != Appointment.Status.COMPLETED:
                appointment.status = Appointment.Status.COMPLETED
                appointment.save(update_fields=['status'])
                
            # Notify patient
            Notification.objects.create(
                recipient=appointment.patient,
                title="Prescription Issued",
                message=f"Dr. {request.user.get_full_name()} has uploaded your prescription for the consultation on {appointment.appointment_date}.",
                notification_type=Notification.NotificationType.REPORT,
                link=f"/appointments/{appointment.id}/prescription/"
            )
            
            messages.success(request, "Prescription saved and patient notified successfully!")
            return redirect('appointments:detail', appointment_id=appointment.id)
    return redirect('appointments:detail', appointment_id=appointment.id)


@login_required
def view_prescription_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    prescription = get_object_or_404(Prescription, appointment=appointment)
    
    user = request.user
    if not (user.is_hospital_admin or appointment.patient == user or appointment.doctor == user):
        raise PermissionDenied("Access restricted.")
        
    return render(request, 'appointments/prescription_slip.html', {
        'appointment': appointment,
        'prescription': prescription,
        'doctor': appointment.doctor,
        'patient': appointment.patient,
    })


@login_required
def cancel_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user
    
    if not (user.is_hospital_admin or appointment.patient == user or appointment.doctor == user):
        raise PermissionDenied("You are not allowed to cancel this appointment.")
        
    if request.method == 'POST':
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=['status'])
        send_appointment_notification(appointment, event_type='CANCELLED')
        messages.info(request, "The appointment has been marked as Cancelled.")
        
    return redirect('appointments:detail', appointment_id=appointment.id)


@login_required
def trigger_reminder_demo_view(request, appointment_id):
    """
    Dedicated view enabling doctors/patients/admins to test-fire an SMS & Email reminder
    for an appointment on demand to demonstrate the reminder engine.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user
    if not (user.is_hospital_admin or appointment.patient == user or appointment.doctor == user):
        raise PermissionDenied("Access restricted.")
        
    send_appointment_notification(appointment, event_type='REMINDER')
    messages.success(
        request,
        f"Reminder triggered! Dispatched SMS to {appointment.patient.phone_number or 'Patient Phone'} and Email to {appointment.patient.email}."
    )
    return redirect('appointments:detail', appointment_id=appointment.id)


@login_required
def notifications_list_view(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, 'appointments/notifications.html', {
        'notifications': notifications,
    })


@login_required
def mark_all_notifications_read_view(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('appointments:notifications')
