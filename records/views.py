import os
import mimetypes
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import MedicalRecord
from .forms import MedicalRecordUploadForm
from appointments.models import Appointment, Notification
from accounts.models import User


def user_can_access_record(user, record):
    """
    RBAC check for secure storage access:
    1. Hospital admin / superuser has global access.
    2. Patient can access their own records.
    3. Doctor can access records of patients with whom they have an active or past appointment.
    """
    if not user.is_authenticated:
        return False
    if user.is_hospital_admin:
        return True
    if user.is_patient and record.patient == user:
        return True
    if user.is_doctor:
        return Appointment.objects.filter(doctor=user, patient=record.patient).exists()
    return False


@login_required
def record_list_view(request):
    user = request.user
    if user.is_patient:
        records = MedicalRecord.objects.filter(patient=user)
    elif user.is_doctor:
        # Patients assigned to this doctor
        patient_ids = Appointment.objects.filter(doctor=user).values_list('patient_id', flat=True).distinct()
        records = MedicalRecord.objects.filter(patient_id__in=patient_ids)
    elif user.is_hospital_admin:
        records = MedicalRecord.objects.all()
    else:
        records = MedicalRecord.objects.none()
        
    return render(request, 'records/record_list.html', {
        'records': records,
    })


@login_required
def upload_record_view(request):
    user = request.user
    patient = user if user.is_patient else None
    
    # If a doctor is uploading for a specific patient
    patient_id = request.GET.get('patient_id')
    if patient_id and (user.is_doctor or user.is_hospital_admin):
        patient = get_object_or_404(User, id=patient_id, role=User.Role.PATIENT)
        
    if not patient and not user.is_patient:
        messages.error(request, "Please specify a patient to upload records for.")
        return redirect('records:list')
        
    if request.method == 'POST':
        form = MedicalRecordUploadForm(request.POST, request.FILES, patient=patient)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.uploaded_by = user
            record.save()
            
            # If uploaded by doctor, notify patient; if uploaded by patient, notify assigned doctors
            if user != patient:
                Notification.objects.create(
                    recipient=patient,
                    title="New Medical Record Uploaded",
                    message=f"Dr. {user.get_full_name()} uploaded a record: '{record.title}'.",
                    notification_type=Notification.NotificationType.REPORT,
                    link=f"/records/{record.id}/"
                )
                
            messages.success(request, f"Medical document '{record.title}' uploaded and encrypted securely!")
            return redirect('records:detail', record_id=record.id)
        else:
            messages.error(request, "Failed to upload document. Please check the file format and size.")
    else:
        form = MedicalRecordUploadForm(patient=patient)
        
    return render(request, 'records/upload_record.html', {
        'form': form,
        'patient': patient,
    })


@login_required
def record_detail_view(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    if not user_can_access_record(request.user, record):
        raise PermissionDenied("Access Denied: You do not have security clearance to inspect this patient medical record.")
        
    return render(request, 'records/record_detail.html', {
        'record': record,
    })


@login_required
def download_record_view(request, record_id):
    """
    Secure file streaming endpoint. Validates role-based permissions before serving
    the raw file from protected storage.
    """
    record = get_object_or_404(MedicalRecord, id=record_id)
    
    if not user_can_access_record(request.user, record):
        return HttpResponseForbidden("403 Forbidden: Security policy restricts access to this medical record.")
        
    if not record.file or not os.path.exists(record.file.path):
        raise Http404("The requested medical file was not found on secure storage.")
        
    content_type, _ = mimetypes.guess_type(record.file.path)
    if not content_type:
        content_type = 'application/octet-stream'
        
    # Check if download or inline viewing is requested
    as_attachment = request.GET.get('download', '1') == '1'
    
    response = FileResponse(open(record.file.path, 'rb'), content_type=content_type)
    filename = os.path.basename(record.file.name)
    disp = 'attachment' if as_attachment else 'inline'
    response['Content-Disposition'] = f'{disp}; filename="{filename}"'
    return response


@login_required
def delete_record_view(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    
    # Only owner or admin can delete
    if not (request.user.is_hospital_admin or record.uploaded_by == request.user or record.patient == request.user):
        raise PermissionDenied("You are not authorized to delete this document.")
        
    if request.method == 'POST':
        title = record.title
        if record.file and os.path.exists(record.file.path):
            try:
                os.remove(record.file.path)
            except OSError:
                pass
        record.delete()
        messages.info(request, f"Medical record '{title}' has been removed.")
        return redirect('records:list')
        
    return redirect('records:detail', record_id=record.id)
