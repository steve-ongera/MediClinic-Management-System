from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view , name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/' , views.admin_dashboard_view , name="admin_dashboard"),
    path('receptionist_dashboard/' , views.receptionist_dashboard , name="receptionist_dashboard"),
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

    #stocks alert
    path('medicines/', views.MedicineStockListView.as_view(), name='medicine_stock_list'),
    path('medicines/<int:pk>/', views.MedicineDetailView.as_view(), name='medicine_detail'),
    path('medicines/low-stock/', views.low_stock_medicines, name='low_stock_medicines'),

    path('medicine-categories/', views.medicine_category_list, name='medicine_category_list'),
    path('medicine-categories/<int:category_id>/', views.medicine_category_detail, name='medicine_category_detail'),
    path('ajax/medicine/<int:pk>/', views.get_medicine_detail, name='ajax-medicine-detail'),
    path('ajax/update-medicine/<int:pk>/', views.update_medicine_ajax, name='update_medicine_ajax'),
    
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

 
    path('doctor/', views.doctor_list, name='doctor_list'),
    path('doctor/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctor/add/', views.doctor_add, name='doctor_add'),
    path('doctor/<int:pk>/edit/', views.doctor_edit, name='doctor_edit'),
    path('doctor/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    path('financial_reports/' , views.financial_reports , name="financial_reports"),
    path('reports/clinical/', views.clinical_reports, name='clinical_reports'),
    path('reports/inventory/', views.inventory_reports, name='inventory_reports'),

    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    path('doctor_calendar_view/' , views.doctor_calendar_view , name="doctor_calendar_view"),
    # Appointment list view
    path('appointments/', views.appointment_list, name='appointment_list'),
    
    # AJAX appointment detail view
    path('appointments/<int:appointment_id>/detail/', views.appointment_detail_ajax, name='appointment_detail_ajax'),
    path('hep-support/', views.help_support, name='help_support'),
    path('clinic-settings/', views.clinic_settings, name='clinic_settings'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('sales/create-from-consultation/', views.CreateMedicineSaleFromConsultation.as_view(), 
         name='create_sale_from_consultation'),

]
