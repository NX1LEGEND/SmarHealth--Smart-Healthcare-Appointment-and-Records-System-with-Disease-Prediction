from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    PatientRegistrationForm,
    DoctorRegistrationForm,
    CustomLoginForm,
    UserProfileUpdateForm,
    PatientMedicalProfileForm,
    DoctorSettingsForm,
)
from .models import User, DoctorProfile, PatientProfile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
        
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name_or_username()}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password. Please verify your credentials.")
    else:
        form = CustomLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been securely logged out.")
    return redirect('core:home')


def register_patient_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
        
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your Patient account has been successfully created!")
            return redirect('core:patient_dashboard')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = PatientRegistrationForm()
        
    return render(request, 'accounts/register_patient.html', {'form': form})


def register_doctor_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
        
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Doctor profile successfully registered for Dr. {user.get_full_name()}!")
            return redirect('core:doctor_dashboard')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = DoctorRegistrationForm()
        
    return render(request, 'accounts/register_doctor.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user
    role_form = None
    
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=user)
        if user.is_patient:
            profile, _ = PatientProfile.objects.get_or_create(user=user)
            role_form = PatientMedicalProfileForm(request.POST, instance=profile)
        elif user.is_doctor:
            profile, _ = DoctorProfile.objects.get_or_create(user=user)
            role_form = DoctorSettingsForm(request.POST, instance=profile)
            
        if user_form.is_valid() and (role_form is None or role_form.is_valid()):
            user_form.save()
            if role_form:
                role_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Failed to update profile. Please check the entered data.")
    else:
        user_form = UserProfileUpdateForm(instance=user)
        if user.is_patient:
            profile, _ = PatientProfile.objects.get_or_create(user=user)
            role_form = PatientMedicalProfileForm(instance=profile)
        elif user.is_doctor:
            profile, _ = DoctorProfile.objects.get_or_create(user=user)
            role_form = DoctorSettingsForm(instance=profile)
            
    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'role_form': role_form,
    })
