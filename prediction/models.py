from django.db import models
from django.conf import settings


class HealthPrediction(models.Model):
    class Disease(models.TextChoices):
        DIABETES = 'DIABETES', 'Diabetes Mellitus Type-2'
        HEART_DISEASE = 'HEART_DISEASE', 'Cardiovascular Heart Disease'

    class RiskLevel(models.TextChoices):
        LOW = 'LOW', 'Low Risk'
        MODERATE = 'MODERATE', 'Moderate Risk'
        HIGH = 'HIGH', 'High Risk'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_predictions',
        limit_choices_to={'role': 'PATIENT'}
    )
    disease_type = models.CharField(
        max_length=30,
        choices=Disease.choices
    )
    risk_score = models.FloatField(help_text="Calculated risk percentage (0-100)")
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices
    )
    prediction_label = models.PositiveSmallIntegerField(
        choices=[(0, 'Negative / Healthy'), (1, 'Positive / Elevated Risk')]
    )
    input_features = models.JSONField(help_text="Key-value pairs of patient inputs")
    contributing_factors = models.JSONField(
        default=list,
        blank=True,
        help_text="List of clinical indicators that contributed to risk"
    )
    recommendations = models.TextField(help_text="Lifestyle, dietary, and medical guidance")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_disease_type_display()} Assessment for {self.patient.get_full_name() or self.patient.username} - {self.risk_level} ({self.risk_score:.1f}%)"

    @property
    def badge_class(self):
        if self.risk_level == self.RiskLevel.HIGH:
            return 'danger'
        elif self.risk_level == self.RiskLevel.MODERATE:
            return 'warning'
        return 'success'
