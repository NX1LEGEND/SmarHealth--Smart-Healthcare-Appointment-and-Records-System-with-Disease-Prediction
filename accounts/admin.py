from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DoctorProfile, PatientProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Healthcare Role & Vitals', {
            'fields': ('role', 'phone_number', 'date_of_birth', 'gender', 'blood_group', 'address', 'profile_picture')
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email')


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'qualification', 'experience_years', 'consultation_fee', 'is_available')
    list_filter = ('specialty', 'is_available')
    search_fields = ('user__first_name', 'user__last_name', 'specialty', 'license_number')


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'emergency_contact_name', 'emergency_contact_phone')
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
