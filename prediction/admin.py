from django.contrib import admin
from .models import HealthPrediction


@admin.register(HealthPrediction)
class HealthPredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'disease_type', 'risk_score', 'risk_level', 'created_at')
    list_filter = ('disease_type', 'risk_level', 'created_at')
    search_fields = ('patient__username', 'disease_type')
