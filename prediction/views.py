import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import HealthPrediction
from .forms import DiabetesPredictionForm, HeartDiseasePredictionForm
from .predictor import predict_diabetes_risk, predict_heart_disease_risk
from appointments.models import Notification
from accounts.models import User, DoctorProfile


def prediction_hub_view(request):
    """Landing portal for AI disease risk assessment models."""
    return render(request, 'prediction/hub.html')


@login_required
def predict_diabetes_view(request):
    patient = request.user if request.user.is_patient else None
    
    # If doctor is running assessment for a patient
    patient_id = request.GET.get('patient_id')
    if patient_id and (request.user.is_doctor or request.user.is_hospital_admin):
        patient = get_object_or_404(User, id=patient_id, role=User.Role.PATIENT)
        
    if request.method == 'POST':
        form = DiabetesPredictionForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            result = predict_diabetes_risk(cleaned_data)
            
            # Save assessment record if patient is identified
            pred_record = None
            if patient:
                pred_record = HealthPrediction.objects.create(
                    patient=patient,
                    disease_type=HealthPrediction.Disease.DIABETES,
                    risk_score=result['risk_score'],
                    risk_level=result['risk_level'],
                    prediction_label=result['prediction_label'],
                    input_features=cleaned_data,
                    contributing_factors=result['contributing_factors'],
                    recommendations=result['recommendations']
                )
                
                # If high risk, notify patient and encourage booking
                if result['risk_level'] == 'HIGH':
                    Notification.objects.create(
                        recipient=patient,
                        title="⚠️ Elevated Diabetes Risk Detected",
                        message=f"Your recent assessment indicates a high preliminary risk ({result['risk_score']}%). We strongly recommend booking a consultation with an Endocrinologist.",
                        notification_type=Notification.NotificationType.PREDICTION,
                        link=f"/prediction/results/{pred_record.id}/"
                    )
                    
            # Find recommended doctors
            specialists = User.objects.filter(
                role=User.Role.DOCTOR,
                doctor_profile__is_available=True,
                doctor_profile__specialty__icontains='Endocrin'
            )[:3]
            if not specialists:
                specialists = User.objects.filter(role=User.Role.DOCTOR, doctor_profile__is_available=True)[:3]
                
            return render(request, 'prediction/result.html', {
                'disease_name': 'Type 2 Diabetes Mellitus',
                'disease_code': 'DIABETES',
                'result': result,
                'inputs': cleaned_data,
                'prediction_record': pred_record,
                'specialists': specialists,
            })
        else:
            messages.error(request, "Please verify the vitals and laboratory values entered.")
    else:
        # Pre-fill age if patient has date of birth
        initial = {}
        if patient and patient.date_of_birth:
            import datetime
            today = datetime.date.today()
            age = today.year - patient.date_of_birth.year
            initial['age'] = age
        form = DiabetesPredictionForm(initial=initial)
        
    return render(request, 'prediction/diabetes_form.html', {
        'form': form,
        'patient': patient,
    })


@login_required
def predict_heart_disease_view(request):
    patient = request.user if request.user.is_patient else None
    
    patient_id = request.GET.get('patient_id')
    if patient_id and (request.user.is_doctor or request.user.is_hospital_admin):
        patient = get_object_or_404(User, id=patient_id, role=User.Role.PATIENT)
        
    if request.method == 'POST':
        form = HeartDiseasePredictionForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            result = predict_heart_disease_risk(cleaned_data)
            
            pred_record = None
            if patient:
                pred_record = HealthPrediction.objects.create(
                    patient=patient,
                    disease_type=HealthPrediction.Disease.HEART_DISEASE,
                    risk_score=result['risk_score'],
                    risk_level=result['risk_level'],
                    prediction_label=result['prediction_label'],
                    input_features=cleaned_data,
                    contributing_factors=result['contributing_factors'],
                    recommendations=result['recommendations']
                )
                
                if result['risk_level'] == 'HIGH':
                    Notification.objects.create(
                        recipient=patient,
                        title="⚠️ Elevated Cardiovascular Risk Detected",
                        message=f"Your preliminary heart health evaluation shows elevated risk ({result['risk_score']}%). Please arrange an appointment with a Cardiologist promptly.",
                        notification_type=Notification.NotificationType.PREDICTION,
                        link=f"/prediction/results/{pred_record.id}/"
                    )
                    
            specialists = User.objects.filter(
                role=User.Role.DOCTOR,
                doctor_profile__is_available=True,
                doctor_profile__specialty__icontains='Cardio'
            )[:3]
            if not specialists:
                specialists = User.objects.filter(role=User.Role.DOCTOR, doctor_profile__is_available=True)[:3]
                
            return render(request, 'prediction/result.html', {
                'disease_name': 'Cardiovascular Heart Disease',
                'disease_code': 'HEART_DISEASE',
                'result': result,
                'inputs': cleaned_data,
                'prediction_record': pred_record,
                'specialists': specialists,
            })
        else:
            messages.error(request, "Please check the values entered in the cardiac evaluation form.")
    else:
        initial = {}
        if patient:
            if patient.gender == 'M':
                initial['sex'] = 1
            elif patient.gender == 'F':
                initial['sex'] = 0
            if patient.date_of_birth:
                import datetime
                today = datetime.date.today()
                initial['age'] = today.year - patient.date_of_birth.year
        form = HeartDiseasePredictionForm(initial=initial)
        
    return render(request, 'prediction/heart_form.html', {
        'form': form,
        'patient': patient,
    })


@login_required
def prediction_detail_view(request, prediction_id):
    prediction = get_object_or_404(HealthPrediction, id=prediction_id)
    user = request.user
    
    # Check permissions
    if not (user.is_hospital_admin or prediction.patient == user or user.is_doctor):
        raise PermissionDenied("You do not have permission to view this medical prediction.")
        
    result = {
        'risk_score': prediction.risk_score,
        'risk_level': prediction.risk_level,
        'prediction_label': prediction.prediction_label,
        'contributing_factors': prediction.contributing_factors,
        'recommendations': prediction.recommendations,
    }
    
    specialty_keyword = 'Cardio' if prediction.disease_type == HealthPrediction.Disease.HEART_DISEASE else 'Endocrin'
    specialists = User.objects.filter(
        role=User.Role.DOCTOR,
        doctor_profile__is_available=True,
        doctor_profile__specialty__icontains=specialty_keyword
    )[:3]
    if not specialists:
        specialists = User.objects.filter(role=User.Role.DOCTOR, doctor_profile__is_available=True)[:3]
        
    return render(request, 'prediction/result.html', {
        'disease_name': prediction.get_disease_type_display(),
        'disease_code': prediction.disease_type,
        'result': result,
        'inputs': prediction.input_features,
        'prediction_record': prediction,
        'specialists': specialists,
    })


@login_required
def prediction_history_view(request):
    user = request.user
    if user.is_patient:
        predictions = HealthPrediction.objects.filter(patient=user)
    elif user.is_doctor or user.is_hospital_admin:
        patient_id = request.GET.get('patient_id')
        if patient_id:
            predictions = HealthPrediction.objects.filter(patient_id=patient_id)
        else:
            predictions = HealthPrediction.objects.all()
    else:
        predictions = HealthPrediction.objects.none()
        
    return render(request, 'prediction/history.html', {
        'predictions': predictions,
    })
