from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    path('', views.prediction_hub_view, name='hub'),
    path('diabetes/', views.predict_diabetes_view, name='diabetes'),
    path('heart/', views.predict_heart_disease_view, name='heart'),
    path('results/<int:prediction_id>/', views.prediction_detail_view, name='detail'),
    path('history/', views.prediction_history_view, name='history'),
]
