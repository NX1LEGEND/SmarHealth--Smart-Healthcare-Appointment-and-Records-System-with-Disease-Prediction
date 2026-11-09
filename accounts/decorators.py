from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def patient_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_patient:
            messages.error(request, "Access restricted to Patient accounts only.")
            return redirect('core:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def doctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_doctor:
            messages.error(request, "Access restricted to Doctor accounts only.")
            return redirect('core:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_hospital_admin:
            messages.error(request, "Access restricted to Hospital Administrators only.")
            return redirect('core:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
