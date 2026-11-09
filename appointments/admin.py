from django.contrib import admin
from .models import Appointment, Prescription, Notification


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'reminder_sent')
    list_filter = ('status', 'appointment_date', 'reminder_sent')
    search_fields = ('patient__username', 'doctor__username', 'patient__first_name', 'doctor__first_name', 'symptoms')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'doctor', 'patient', 'created_at')
    search_fields = ('patient__username', 'doctor__username', 'diagnosis')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
