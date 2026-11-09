from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    path('', views.record_list_view, name='list'),
    path('upload/', views.upload_record_view, name='upload'),
    path('<int:record_id>/', views.record_detail_view, name='detail'),
    path('<int:record_id>/download/', views.download_record_view, name='download'),
    path('<int:record_id>/delete/', views.delete_record_view, name='delete'),
]
