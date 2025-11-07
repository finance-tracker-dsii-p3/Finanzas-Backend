from django.urls import path
from . import views

app_name = 'export'

urlpatterns = [
    # Trabajos de exportación - versión simplificada
    path('jobs/', views.ExportJobListCreateView.as_view(), name='export-job-list-create'),
    path('jobs/<int:pk>/', views.ExportJobDetailView.as_view(), name='export-job-detail'),
    path('jobs/<int:export_id>/download/', views.download_export, name='download-export'),
    
    # Exportación básica de datos
    path('create/', views.create_basic_export, name='create-basic-export'),
    path('users/data/', views.get_users_data, name='get-users-data'),
]

