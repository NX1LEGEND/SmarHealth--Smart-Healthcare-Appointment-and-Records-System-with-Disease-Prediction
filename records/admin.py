from django.contrib import admin
from .models import MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'patient', 'record_type', 'record_date', 'file_size_display', 'uploaded_by', 'created_at')
    list_filter = ('record_type', 'record_date')
    search_fields = ('title', 'patient__username', 'notes')
