from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view , name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/' , views.admin_dashboard_view , name="admin_dashboard"),
    path('patients/', views.patient_list, name='patients-list'),
    path('patients/create/', views.patient_create, name='create'),
    path('patients/<int:pk>/update/', views.patient_update, name='update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='delete'),
    
    # AJAX URLs
    path('api/<int:pk>/detail/', views.patient_detail_ajax, name='detail_ajax'),
    path('api/<int:pk>/update/', views.update_patient_ajax, name='update_ajax'),
    path('api/<int:pk>/delete/', views.delete_patient_ajax, name='delete_ajax'),
]
