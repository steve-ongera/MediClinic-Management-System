from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone

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

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Doctor(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Prefer Not to Say'),
    )
    
    BLOOD_TYPE_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    
    SPECIALIZATION_CHOICES = (
        ('GP', 'General Practitioner'),
        ('CAR', 'Cardiologist'),
        ('DER', 'Dermatologist'),
        ('PED', 'Pediatrician'),
        ('ORT', 'Orthopedic Surgeon'),
        ('NEU', 'Neurologist'),
        ('PSY', 'Psychiatrist'),
        ('ONC', 'Oncologist'),
        ('RAD', 'Radiologist'),
        ('EM', 'Emergency Medicine'),
        ('ANES', 'Anesthesiologist'),
        ('OBGYN', 'Obstetrician/Gynecologist'),
        ('ENT', 'ENT Specialist'),
    )
    
    # Personal Information
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date_of_birth = models.DateField(_("Date of Birth"))
    gender = models.CharField(_("Gender"), max_length=1, choices=GENDER_CHOICES)
    id_number = models.CharField(_("ID Number"), max_length=20, unique=True)
    national_id = models.CharField(_("National ID"), max_length=20, blank=True, null=True)
    passport_number = models.CharField(_("Passport Number"), max_length=20, blank=True, null=True)
    
    # Contact Information
    phone_number = models.CharField(_("Phone Number"), max_length=15)
    alternate_phone = models.CharField(_("Alternate Phone"), max_length=15, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    emergency_contact = models.CharField(_("Emergency Contact"), max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(_("Emergency Phone"), max_length=15, blank=True, null=True)
    
    # Address Information
    address = models.TextField(_("Address"), blank=True, null=True)
    city = models.CharField(_("City"), max_length=100, blank=True, null=True)
    state = models.CharField(_("State/Province"), max_length=100, blank=True, null=True)
    country = models.CharField(_("Country"), max_length=100, blank=True, null=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True, null=True)
    
    # Medical Information
    blood_type = models.CharField(_("Blood Type"), max_length=5, choices=BLOOD_TYPE_CHOICES, blank=True, null=True)
    allergies = models.TextField(_("Allergies"), blank=True, null=True)
    chronic_conditions = models.TextField(_("Chronic Conditions"), blank=True, null=True)
    
    # Professional Information
    specialization = models.CharField(_("Specialization"), max_length=10, choices=SPECIALIZATION_CHOICES)
    license_number = models.CharField(_("Medical License Number"), max_length=50, unique=True)
    license_expiry = models.DateField(_("License Expiry Date"), blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(_("Years of Experience"), validators=[MinValueValidator(0), MaxValueValidator(100)])
    qualifications = models.TextField(_("Qualifications"), blank=True, null=True)
    bio = models.TextField(_("Professional Bio"), blank=True, null=True)
    
    # Hospital/Clinic Affiliation
    is_active = models.BooleanField(_("Active Staff"), default=True)
    joining_date = models.DateField(_("Joining Date"), blank=True, null=True)
    department = models.CharField(_("Department"), max_length=100, blank=True, null=True)
    position = models.CharField(_("Position"), max_length=100, blank=True, null=True)
    
    # System Information
    profile_picture = models.ImageField(_("Profile Picture"), upload_to='doctors/profile_pictures/', blank=True, null=True)
    signature = models.ImageField(_("Signature"), upload_to='doctors/signatures/', blank=True, null=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    # Availability (could be moved to separate model if complex)
    working_days = models.CharField(_("Working Days"), max_length=100, blank=True, null=True,
                                  help_text="Comma separated days (e.g., Mon,Tue,Wed)")
    working_hours = models.CharField(_("Working Hours"), max_length=100, blank=True, null=True,
                                   help_text="e.g., 9:00 AM - 5:00 PM")
    
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} ({self.get_specialization_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        import datetime
        return datetime.date.today().year - self.date_of_birth.year - (
            (datetime.date.today().month, datetime.date.today().day) < 
            (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def license_status(self):
        if not self.license_expiry:
            return "Unknown"
        from datetime import date
        return "Valid" if self.license_expiry >= date.today() else "Expired"
    
    class Meta:
        verbose_name = _("Doctor")
        verbose_name_plural = _("Doctors")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['specialization']),
            models.Index(fields=['license_number']),
        ]


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Nurse(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Prefer Not to Say'),
    )
    
    BLOOD_TYPE_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    
    NURSE_TYPE_CHOICES = (
        ('RN', 'Registered Nurse'),
        ('LPN', 'Licensed Practical Nurse'),
        ('NP', 'Nurse Practitioner'),
        ('CNS', 'Clinical Nurse Specialist'),
        ('CRNA', 'Certified Registered Nurse Anesthetist'),
        ('CNM', 'Certified Nurse Midwife'),
        ('SN', 'Student Nurse'),
    )
    
    DEPARTMENT_CHOICES = (
        ('ER', 'Emergency Room'),
        ('ICU', 'Intensive Care Unit'),
        ('OR', 'Operating Room'),
        ('PED', 'Pediatrics'),
        ('OB', 'Obstetrics'),
        ('ONC', 'Oncology'),
        ('CAR', 'Cardiology'),
        ('PSY', 'Psychiatry'),
        ('GEN', 'General Ward'),
        ('OPD', 'Outpatient Department'),
    )
    
    # Personal Information
    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    date_of_birth = models.DateField(_("Date of Birth"))
    gender = models.CharField(_("Gender"), max_length=1, choices=GENDER_CHOICES)
    national_id = models.CharField(_("National ID"), max_length=20, blank=True, null=True)
    nurse_id = models.CharField(_("Nurse ID"), max_length=20, unique=True)
    
    # Contact Information
    phone_number = models.CharField(_("Phone Number"), max_length=15)
    alternate_phone = models.CharField(_("Alternate Phone"), max_length=15, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    emergency_contact = models.CharField(_("Emergency Contact"), max_length=100, blank=True, null=True)
    emergency_relation = models.CharField(_("Relationship"), max_length=50, blank=True, null=True)
    emergency_phone = models.CharField(_("Emergency Phone"), max_length=15, blank=True, null=True)
    
    # Address Information
    address = models.TextField(_("Address"), blank=True, null=True)
    city = models.CharField(_("City"), max_length=100, blank=True, null=True)
    state = models.CharField(_("State/Province"), max_length=100, blank=True, null=True)
    country = models.CharField(_("Country"), max_length=100, blank=True, null=True)
    postal_code = models.CharField(_("Postal Code"), max_length=20, blank=True, null=True)
    
    # Medical Information
    blood_type = models.CharField(_("Blood Type"), max_length=5, choices=BLOOD_TYPE_CHOICES, blank=True, null=True)
    allergies = models.TextField(_("Allergies"), blank=True, null=True)
    chronic_conditions = models.TextField(_("Chronic Conditions"), blank=True, null=True)
    
    # Professional Information
    nurse_type = models.CharField(_("Nurse Type"), max_length=5, choices=NURSE_TYPE_CHOICES)
    license_number = models.CharField(_("License Number"), max_length=50, unique=True)
    license_expiry = models.DateField(_("License Expiry Date"), blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(
        _("Years of Experience"), 
        validators=[MinValueValidator(0), MaxValueValidator(60)],
        default=0
    )
    department = models.CharField(_("Department"), max_length=5, choices=DEPARTMENT_CHOICES)
    specialization = models.CharField(_("Specialization"), max_length=100, blank=True, null=True)
    certifications = models.TextField(_("Certifications"), blank=True, null=True)
    bio = models.TextField(_("Professional Bio"), blank=True, null=True)
    
    # Employment Details
    is_active = models.BooleanField(_("Active Staff"), default=True)
    joining_date = models.DateField(_("Joining Date"), blank=True, null=True)
    position = models.CharField(_("Position"), max_length=100, blank=True, null=True)
    shift_pattern = models.CharField(_("Shift Pattern"), max_length=100, blank=True, null=True)
    is_charge_nurse = models.BooleanField(_("Charge Nurse"), default=False)
    
    # Skills and Competencies
    is_bcls_certified = models.BooleanField(_("BCLS Certified"), default=False)
    is_acl_certified = models.BooleanField(_("ACLS Certified"), default=False)
    is_pals_certified = models.BooleanField(_("PALS Certified"), default=False)
    additional_skills = models.TextField(_("Additional Skills"), blank=True, null=True)
    
    # System Information
    profile_picture = models.ImageField(
        _("Profile Picture"), 
        upload_to='nurses/profile_pictures/', 
        blank=True, 
        null=True
    )
    signature = models.ImageField(
        _("Signature"), 
        upload_to='nurses/signatures/', 
        blank=True, 
        null=True
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    def __str__(self):
        return f"Nurse {self.first_name} {self.last_name} ({self.get_nurse_type_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        import datetime
        return datetime.date.today().year - self.date_of_birth.year - (
            (datetime.date.today().month, datetime.date.today().day) < 
            (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def license_status(self):
        if not self.license_expiry:
            return "Unknown"
        from datetime import date
        return "Valid" if self.license_expiry >= date.today() else "Expired"
    
    class Meta:
        verbose_name = _("Nurse")
        verbose_name_plural = _("Nurses")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['nurse_type']),
            models.Index(fields=['department']),
            models.Index(fields=['license_number']),
        ]

        
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

import random
import string

class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    diseases = models.ManyToManyField(Disease, blank=True)
    notes = models.TextField(blank=True, null=True)
    follow_up_date = models.DateField(blank=True, null=True)
    follow_up_notes = models.TextField(blank=True, null=True)
    consultation_code = models.CharField(max_length=10, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consultation for {self.appointment.patient} on {self.created_at.date()}"

    def generate_unique_code(self):
        while True:
            code = 'R' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            if not Consultation.objects.filter(consultation_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if not self.consultation_code:
            self.consultation_code = self.generate_unique_code()
        super().save(*args, **kwargs)


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
    sale_date = models.DateTimeField(default=timezone.now)  # instead of auto_now_add=True
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

class DoctorSchedule(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_patients = models.IntegerField(default=20)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['doctor', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
    

class DoctorLeave(models.Model):
    LEAVE_TYPE = [
        ('sick', 'Sick Leave'),
        ('vacation', 'Vacation'),
        ('conference', 'Conference'),
        ('emergency', 'Emergency'),
        ('other', 'Other'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE)
    reason = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.doctor} - {self.leave_type} ({self.start_date} to {self.end_date})"
    


class WorkloadSummary(models.Model):
    """Daily workload summary for doctors"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    total_appointments = models.IntegerField(default=0)
    completed_appointments = models.IntegerField(default=0)
    cancelled_appointments = models.IntegerField(default=0)
    total_hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    workload_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['doctor', 'date']
    
    def __str__(self):
        return f"{self.doctor} - {self.date} ({self.workload_percentage}% workload)"
    

from django.db import models
from django.utils import timezone
import uuid


class OverTheCounterSale(models.Model):
    """
    Model for tracking over-the-counter medicine sales where detailed patient 
    information is not required.
    """
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    sale_id = models.CharField(max_length=50, unique=True, editable=False)
    customer_name = models.CharField(max_length=100)
    mpesa_code = models.CharField(max_length=20, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    cashier = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='otc_sales')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Generate a unique sale ID if not already set
        if not self.sale_id:
            today = timezone.now().strftime('%Y%m%d')
            self.sale_id = f"OTC-{today}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.sale_id} - {self.customer_name}"
    
    @property
    def get_items_count(self):
        return self.items.count()
    
    @property
    def get_items(self):
        return self.items.all()


class OverTheCounterSaleItem(models.Model):
    """
    Model for tracking individual medicine items in an over-the-counter sale.
    """
    sale = models.ForeignKey(OverTheCounterSale, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey('Medicine', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Calculate subtotal before saving
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity} x {self.medicine.name}"
    
    class Meta:
        ordering = ['created_at']


class Conversation(models.Model):
    participant1 = models.ForeignKey(User, related_name='conversations_as_participant1', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(User, related_name='conversations_as_participant2', on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('participant1', 'participant2', 'patient')

    def __str__(self):
        return f"Conversation between {self.participant1} and {self.participant2}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"

class ReceptionQueue(models.Model):
    receptionist = models.ForeignKey(User, on_delete=models.CASCADE)
    current_patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Queue for {self.receptionist}"