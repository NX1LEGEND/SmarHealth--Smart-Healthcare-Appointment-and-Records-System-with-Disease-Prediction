from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/patient/', views.register_patient_view, name='register_patient'),
    path('register/doctor/', views.register_doctor_view, name='register_doctor'),
    path('profile/', views.profile_view, name='profile'),
]
