from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),
    path('dashboard/patient/', views.patient_dashboard_view, name='patient_dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
]
