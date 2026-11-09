from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('doctors/', views.doctor_directory_view, name='doctor_directory'),
    path('doctors/<int:doctor_id>/', views.doctor_detail_view, name='doctor_detail'),
    path('book/', views.book_appointment_view, name='book'),
    path('<int:appointment_id>/', views.appointment_detail_view, name='detail'),
    path('<int:appointment_id>/status/', views.update_appointment_status_view, name='update_status'),
    path('<int:appointment_id>/prescription/', views.create_prescription_view, name='create_prescription'),
    path('<int:appointment_id>/prescription/view/', views.view_prescription_view, name='view_prescription'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment_view, name='cancel'),
    path('<int:appointment_id>/trigger-reminder/', views.trigger_reminder_demo_view, name='trigger_reminder'),
    path('notifications/', views.notifications_list_view, name='notifications'),
    path('notifications/read-all/', views.mark_all_notifications_read_view, name='mark_notifications_read'),
]
