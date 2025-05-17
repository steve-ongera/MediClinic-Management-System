from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('DOCTOR', 'Doctor'),
        ('RECEPTIONIST', 'Receptionist'),
    )
    
    user_type = models.CharField(max_length=12, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)  # For doctors
    license_number = models.CharField(max_length=50, blank=True, null=True)  # For doctors
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"

class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    id_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    blood_type = models.CharField(max_length=5, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.id_number})"
    
    class Meta:
        ordering = ['-created_at']

class Disease(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    icd_code = models.CharField(max_length=20, blank=True, null=True)  # International Classification of Diseases code
    
    def __str__(self):
        return self.name

class MedicineCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey('MedicineCategory', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.PositiveIntegerField(default=10)
    manufacturer = models.CharField(max_length=200, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='medicine_images/', blank=True, null=True)  # ✅ New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.quantity_in_stock} in stock)"
    
    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'DOCTOR'})
    receptionist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='booked_appointments', limit_choices_to={'user_type': 'RECEPTIONIST'})
    scheduled_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    reason = models.TextField()
    symptoms = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient} with Dr. {self.doctor.last_name} at {self.scheduled_time}"
    
    class Meta:
        ordering = ['scheduled_time']

class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    diseases = models.ManyToManyField(Disease, blank=True)
    notes = models.TextField(blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)
    follow_up_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Consultation for {self.appointment.patient} on {self.created_at.date()}"

class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)  # e.g., "7 days", "2 weeks"
    instructions = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    prescribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.medicine.name} for {self.consultation.appointment.patient}"

class MedicineSale(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('MPESA', 'M-Pesa'),
        ('INSURANCE', 'Insurance'),
        ('CREDIT', 'Credit'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    receptionist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'RECEPTIONIST'})
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    mpesa_number = models.CharField(max_length=15, blank=True, null=True)
    mpesa_code = models.CharField(max_length=50, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Sale #{self.id} - {self.total_amount}"
    
    class Meta:
        ordering = ['-sale_date']

class SoldMedicine(models.Model):
    sale = models.ForeignKey(MedicineSale, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.medicine.name} in Sale #{self.sale.id}"
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price

class PatientMedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, blank=True, null=True)
    record_type = models.CharField(max_length=100)  # e.g., "Allergy", "Surgery", "Chronic Condition"
    description = models.TextField()
    date_recorded = models.DateField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.record_type} for {self.patient}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('APPOINTMENT', 'New Appointment'),
        ('LOW_STOCK', 'Low Stock Alert'),
        ('FOLLOW_UP', 'Follow Up Reminder'),
        ('GENERAL', 'General Notification'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    related_object_id = models.PositiveIntegerField(blank=True, null=True)  # Generic relation to any model
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient}"
    
    class Meta:
        ordering = ['-created_at']

class ClinicSettings(models.Model):
    clinic_name = models.CharField(max_length=200)
    clinic_logo = models.ImageField(upload_to='clinic_logos/', blank=True, null=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    working_hours = models.TextField()
    appointment_duration = models.PositiveIntegerField(default=30, help_text="Default appointment duration in minutes")
    max_patients_per_day = models.PositiveIntegerField(default=20)
    
    def __str__(self):
        return self.clinic_name
    
    class Meta:
        verbose_name_plural = "Clinic Settings"