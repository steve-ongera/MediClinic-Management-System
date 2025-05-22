from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Patient, Disease, MedicineCategory, Medicine, 
    Appointment, Consultation, Prescription, MedicineSale, 
    SoldMedicine, PatientMedicalHistory, Notification, ClinicSettings
)

# User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Professional info', {'fields': ('user_type', 'specialization', 'license_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')

admin.site.register(User, CustomUserAdmin)

# Patient Admin
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id_number', 'first_name', 'last_name', 'phone_number', 'gender', 'date_of_birth')
    list_filter = ('gender', 'created_at')
    search_fields = ('first_name', 'last_name', 'id_number', 'phone_number')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'id_number')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Medical Information', {
            'fields': ('blood_type', 'allergies')
        }),
    )

# Disease Admin
@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'icd_code')
    search_fields = ('name', 'icd_code')

# Medicine Category Admin
@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Medicine Admin
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity_in_stock', 'unit_price', 'is_low_stock', 'expiry_date')
    list_filter = ('category', 'manufacturer')
    search_fields = ('name', 'description', 'batch_number')
    date_hierarchy = 'created_at'
    readonly_fields = ('is_low_stock',)#'image'
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'image','category', 'description')
        }),
        ('Stock Information', {
            'fields': ('quantity_in_stock', 'unit_price', 'reorder_level', 'is_low_stock')
        }),
        ('Manufacturer Details', {
            'fields': ('manufacturer', 'expiry_date', 'batch_number')
        }),
    )

# Appointment Admin
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'scheduled_time', 'end_time', 'status')
    list_filter = ('status', 'scheduled_time', 'doctor')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name', 'reason')
    date_hierarchy = 'scheduled_time'
    raw_id_fields = ('patient', 'doctor', 'receptionist')
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'doctor', 'receptionist', 'scheduled_time', 'end_time', 'status')
        }),
        ('Medical Information', {
            'fields': ('reason', 'symptoms')
        }),
    )

# Consultation Admin
class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 1
    raw_id_fields = ('medicine',)

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_patient_name', 'get_doctor_name', 'created_at', 'follow_up_date')
    list_filter = ('follow_up_date', 'created_at')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name', 'diagnosis')
    raw_id_fields = ('appointment',)
    inlines = [PrescriptionInline]
    date_hierarchy = 'created_at'
    filter_horizontal = ('diseases',)
    
    def get_patient_name(self, obj):
        return f"{obj.appointment.patient.first_name} {obj.appointment.patient.last_name}"
    get_patient_name.short_description = 'Patient'
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.appointment.doctor.last_name}"
    get_doctor_name.short_description = 'Doctor'

# Medicine Sale Admin
class SoldMedicineInline(admin.TabularInline):
    model = SoldMedicine
    extra = 1
    raw_id_fields = ('medicine',)

@admin.register(MedicineSale)
class MedicineSaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'payment_method', 'total_amount', 'sale_date')
    list_filter = ('payment_method', 'sale_date')
    search_fields = ('patient__first_name', 'patient__last_name', 'mpesa_code')
    raw_id_fields = ('patient', 'receptionist' )
    inlines = [SoldMedicineInline]
    date_hierarchy = 'sale_date'

# Patient Medical History Admin
@admin.register(PatientMedicalHistory)
class PatientMedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('record_type', 'patient', 'date_recorded', 'recorded_by')
    list_filter = ('record_type', 'date_recorded')
    search_fields = ('patient__first_name', 'patient__last_name', 'description')
    raw_id_fields = ('patient', 'consultation', 'recorded_by')
    date_hierarchy = 'date_recorded'

# Notification Admin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'recipient', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'message')
    date_hierarchy = 'created_at'

# Clinic Settings Admin
@admin.register(ClinicSettings)
class ClinicSettingsAdmin(admin.ModelAdmin):
    list_display = ('clinic_name', 'phone_number', 'email')
    fieldsets = (
        ('Basic Information', {
            'fields': ('clinic_name', 'clinic_logo', 'address')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Operational Settings', {
            'fields': ('working_hours', 'appointment_duration', 'max_patients_per_day')
        }),
    )
    
    def has_add_permission(self, request):
        # Check if there's already a clinic settings object
        return ClinicSettings.objects.count() == 0
    



from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'specialization', 'license_number', 'license_status',
        'phone_number', 'email', 'is_active', 'created_at'
    )
    list_filter = (
        'specialization', 'gender', 'is_active', 'blood_type', 'department',
    )
    search_fields = (
        'first_name', 'last_name', 'id_number', 'license_number', 'phone_number', 'email',
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'license_status', 'age')

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'user', 'date_of_birth', 'gender', 'id_number',
                       'national_id', 'passport_number', 'blood_type', 'age')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'alternate_phone', 'email',
                       'emergency_contact', 'emergency_phone')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Medical Info', {
            'fields': ('allergies', 'chronic_conditions')
        }),
        ('Professional Details', {
            'fields': ('specialization', 'license_number', 'license_expiry', 'license_status',
                       'years_of_experience', 'qualifications', 'bio',
                       'department', 'position', 'is_active', 'joining_date')
        }),
        ('Working Schedule', {
            'fields': ('working_days', 'working_hours')
        }),
        ('Media', {
            'fields': ('profile_picture', 'signature')
        }),
        ('System Info', {
            'fields': ('created_at', 'updated_at')
        }),
    )


from django.contrib import admin
from .models import Nurse

@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'nurse_type', 'department', 'license_number', 'license_status',
        'phone_number', 'email', 'is_active', 'is_charge_nurse', 'created_at'
    )
    list_filter = (
        'nurse_type', 'department', 'gender', 'is_active',
        'is_bcls_certified', 'is_acl_certified', 'is_pals_certified'
    )
    search_fields = (
        'first_name', 'last_name', 'nurse_id', 'license_number', 'phone_number', 'email',
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'license_status', 'age')

    fieldsets = (
        ('Personal Information', {
            'fields': (
                'first_name', 'last_name', 'date_of_birth', 'gender', 'nurse_id',
                'national_id', 'blood_type', 'age'
            )
        }),
        ('Contact Information', {
            'fields': (
                'phone_number', 'alternate_phone', 'email',
                'emergency_contact', 'emergency_relation', 'emergency_phone'
            )
        }),
        ('Address', {
            'fields': (
                'address', 'city', 'state', 'country', 'postal_code'
            )
        }),
        ('Medical Info', {
            'fields': (
                'allergies', 'chronic_conditions'
            )
        }),
        ('Professional Details', {
            'fields': (
                'nurse_type', 'department', 'specialization', 'license_number', 'license_expiry',
                'license_status', 'years_of_experience', 'certifications', 'bio'
            )
        }),
        ('Employment Details', {
            'fields': (
                'position', 'shift_pattern', 'is_charge_nurse', 'is_active', 'joining_date'
            )
        }),
        ('Skills & Competencies', {
            'fields': (
                'is_bcls_certified', 'is_acl_certified', 'is_pals_certified', 'additional_skills'
            )
        }),
        ('Media', {
            'fields': (
                'profile_picture', 'signature'
            )
        }),
        ('System Info', {
            'fields': (
                'created_at', 'updated_at'
            )
        }),
    )


from django.contrib import admin
from .models import OverTheCounterSale, OverTheCounterSaleItem


class OverTheCounterSaleItemInline(admin.TabularInline):
    model = OverTheCounterSaleItem
    extra = 1
    readonly_fields = ('subtotal',)
    fields = ('medicine', 'quantity', 'unit_price', 'subtotal')


@admin.register(OverTheCounterSale)
class OverTheCounterSaleAdmin(admin.ModelAdmin):
    list_display = (
        'sale_id',
        'customer_name',
        'total_amount',
        'payment_status',
        'cashier',
        'created_at',
        'updated_at',
        'get_items_count',
    )
    list_filter = ('payment_status', 'created_at', 'cashier')
    search_fields = ('sale_id', 'customer_name', 'mpesa_code', 'cashier__username')
    readonly_fields = ('sale_id', 'created_at', 'updated_at')
    inlines = [OverTheCounterSaleItemInline]


@admin.register(OverTheCounterSaleItem)
class OverTheCounterSaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'medicine', 'quantity', 'unit_price', 'subtotal', 'created_at')
    list_filter = ('created_at', 'medicine')
    search_fields = ('sale__sale_id', 'medicine__name')
    readonly_fields = ('subtotal',)

