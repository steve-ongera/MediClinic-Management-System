from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view , name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/' , views.admin_dashboard_view , name="admin_dashboard"),
    path('patients/', views.patient_list, name='patients-list'),
    path('patients/create/', views.patient_create, name='patients-create'),
    path('patients/<int:pk>/update/', views.patient_update, name='update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='delete'),
    
    # AJAX URLs
    path('patients/api/<int:pk>/detail/', views.patient_detail_ajax, name='detail_ajax'),
    path('api/<int:pk>/update/', views.update_patient_ajax, name='update_ajax'),
    path('api/<int:pk>/delete/', views.delete_patient_ajax, name='delete_ajax'),


    # Medicine URLs
    path('medicine/', views.MedicineListView.as_view(), name='medicine-list'),
    path('medicine/create/', views.MedicineCreateView.as_view(), name='medicine-create'),
    path('medicine/<int:pk>/', views.MedicineDetailView.as_view(), name='medicine-detail'),
    path('medicine/<int:pk>/edit/', views.MedicineUpdateView.as_view(), name='medicine-update'),
    path('medicine/<int:pk>/delete/', views.MedicineDeleteView.as_view(), name='medicine-delete'),
    path('medicine/api/<int:pk>/', views.medicine_detail_api, name='medicine_api'),
    
    # Category URLs
    path('medicine/categories/', views.CategoryListView.as_view(), name='category_list'),
    path('medicine/categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('medicine/categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('medicine/categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # AJAX endpoint for patient search
    path('patient/search/', views.patient_search_ajax, name='patient_search_ajax'),
    
    # Main consultation form view
    path('consultation/new/', views.consultation_view, name='new_consultation'),
    path('consultation/<int:pk>/', views.consultation_detail, name='consultation_detail'), 
     path('consultations/', views.consultation_list, name='consultation_list'),
    path('consultations/delete/<int:pk>/', views.delete_consultation, name='delete_consultation'),

    path('medicine-sales/', views.medicine_sales_list, name='medicine_sales_list'),
    path('medicine-sales/<int:pk>/', views.medicine_sale_detail, name='medicine_sale_detail'),

    # All medical records (for staff/doctors)
    path('medical-records/', views.all_medical_records, name='all_medical_records'),
    
    # Patient-specific medical history
    path('patients/<int:patient_id>/medical-history/', views.patient_medical_history, name='patient_medical_history'),
]
