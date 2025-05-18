# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views import View
from .forms import CustomLoginForm
from django.contrib.auth import logout
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count, Sum, F, DateTimeField
from django.db.models.functions import Trunc
from datetime import datetime, timedelta
from django.utils import timezone
import json

from .models import *



def login_view(request):
    template_name = 'auth/login.html'
    
    # Handle GET request
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect_user_by_type(request.user)
        form = CustomLoginForm()
        return render(request, template_name, {'form': form})
    
    # Handle POST request
    form = CustomLoginForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name()}!")
                return redirect_user_by_type(user)
            else:
                messages.error(request, "Your account is inactive. Please contact the administrator.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, template_name, {'form': form})


def redirect_user_by_type(user):
    """
    Redirects users to their respective dashboard based on user type
    """
    if user.user_type == 'ADMIN':
        return redirect('admin_dashboard')
    elif user.user_type == 'DOCTOR':
        return redirect('doctor_dashboard')
    elif user.user_type == 'RECEPTIONIST':
        return redirect('receptionist_dashboard')
    else:
        # Fallback for any other user type
        return redirect('home')




def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')  # Change 'login' to your login view name or URL



def admin_dashboard_view(request):
    date_filter = request.GET.get('date_filter', 'month')
    
    if date_filter == 'week':
        start_date = timezone.now() - timedelta(days=7)
    elif date_filter == 'month':
        start_date = timezone.now() - timedelta(days=30)
    elif date_filter == 'quarter':
        start_date = timezone.now() - timedelta(days=90)
    elif date_filter == 'year':
        start_date = timezone.now() - timedelta(days=365)
    else:
        start_date = timezone.now() - timedelta(days=30)  # Default to month

    # Summary data
    total_patients = Patient.objects.count()
    total_doctors = User.objects.filter(user_type='DOCTOR').count()
    total_medicines = Medicine.objects.count()
    total_revenue = MedicineSale.objects.aggregate(total=Sum('total_amount'))['total'] or 0

    # Top 5 diseases
    common_diseases = Disease.objects.annotate(
        count=Count('consultation')
    ).order_by('-count')[:5]
    
    disease_labels = [d.name for d in common_diseases]
    disease_counts = [d.count for d in common_diseases]

    # Top 5 best-selling medicines
    best_selling = SoldMedicine.objects.values('medicine__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    medicine_labels = [item['medicine__name'] for item in best_selling]
    medicine_counts = [item['total_sold'] for item in best_selling]

    # Line chart sales data - LAST 7 DAYS ONLY
    last_7_days = timezone.now() - timedelta(days=7)
    sales_data = MedicineSale.objects.filter(
        sale_date__gte=last_7_days
    ).annotate(
        date=Trunc('sale_date', 'day', output_field=DateTimeField())
    ).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')

    sales_dates = [item['date'].strftime('%Y-%m-%d') for item in sales_data]
    sales_amounts = [float(item['total']) for item in sales_data]

    # Payment method stats - still using the selected date filter
    payment_methods = MedicineSale.objects.filter(
        sale_date__gte=start_date
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('-total')

    payment_labels = [p['payment_method'] for p in payment_methods]
    payment_totals = [float(p['total']) for p in payment_methods]

    # Recent appointments
    recent_appointments = Appointment.objects.select_related(
        'patient', 'doctor'
    ).order_by('-scheduled_time')[:5]

    # Low stock medicines
    low_stock = Medicine.objects.filter(
        quantity_in_stock__lte=F('reorder_level')
    ).order_by('quantity_in_stock')[:5]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_medicines': total_medicines,
        'total_revenue': total_revenue,
        'date_filter': date_filter,
        'disease_labels': json.dumps(disease_labels),
        'disease_counts': json.dumps(disease_counts),
        'medicine_labels': json.dumps(medicine_labels),
        'medicine_counts': json.dumps(medicine_counts),
        'sales_dates': json.dumps(sales_dates),
        'sales_amounts': json.dumps(sales_amounts),
        'payment_labels': json.dumps(payment_labels),
        'payment_totals': json.dumps(payment_totals),
        'recent_appointments': recent_appointments,
        'low_stock': low_stock,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
import datetime
from .models import Patient
from .forms import PatientForm

def patient_list(request):
    """View function for listing all patients with pagination."""
    patients_list = Patient.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        patients_list = patients_list.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(id_number__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(patients_list, 10)  # Show 10 patients per page
    page = request.GET.get('page')
    patients = paginator.get_page(page)
    
    context = {
        'patients': patients
    }
    return render(request, 'patients/patient_list.html', context)

def patient_create(request):
    """View function for creating a new patient."""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient record created successfully!')
            return redirect('patients-list')
    else:
        form = PatientForm()
    
    context = {
        'form': form,
        'is_create': True
    }
    return render(request, 'patients/patient_form.html', context)

def patient_update(request, pk):
    """View function for updating an existing patient."""
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient record updated successfully!')
            return redirect('patients:list')
    else:
        form = PatientForm(instance=patient)
    
    context = {
        'form': form,
        'patient': patient,
        'is_update': True
    }
    return render(request, 'patients/patient_form.html', context)

def patient_delete(request, pk):
    """View function for deleting a patient."""
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Patient record deleted successfully!')
        return redirect('patients:list')
    
    context = {
        'patient': patient
    }
    return render(request, 'patients/patient_confirm_delete.html', context)

def patient_detail_ajax(request, pk):
    """View function for retrieving patient details via AJAX."""
    import datetime  # Correct import method 1
    # OR use: from datetime import date  # Correct import method 2
    
    patient = get_object_or_404(Patient, pk=pk)
    
    # Calculate age - fixed datetime usage
    today = datetime.date.today()  # If using import datetime
    # OR use: today = date.today()  # If using from datetime import date
    
    age = today.year - patient.date_of_birth.year - (
        (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
    )
    
    data = {
        'id': patient.id,
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'full_name': f"{patient.first_name} {patient.last_name}",
        'gender': patient.get_gender_display(),
        'gender_code': patient.gender,
        'age': age,
        'gender_age': f"{patient.get_gender_display()} • {age} years",
        'id_number': patient.id_number,
        'phone_number': patient.phone_number,
        'email': patient.email or "No email provided",
        'address': patient.address or "No address provided",
        'blood_type': patient.blood_type or "Not specified",
        'allergies': patient.allergies or "No allergies recorded",
        'date_of_birth': patient.date_of_birth.strftime('%B %d, %Y'),
        'dob_iso': patient.date_of_birth.strftime('%Y-%m-%d'),
        'created_at': patient.created_at.strftime('%B %d, %Y'),
        'updated_at': patient.updated_at.strftime('%B %d, %Y'),
    }
    
    return JsonResponse(data)

def update_patient_ajax(request, pk):
    """View function for updating patient details via AJAX."""
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Patient updated successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def delete_patient_ajax(request, pk):
    """View function for deleting patient via AJAX."""
    if request.method == 'POST':
        patient = get_object_or_404(Patient, pk=pk)
        patient.delete()
        return JsonResponse({'success': True, 'message': 'Patient deleted successfully'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)



from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Medicine, MedicineCategory


class MedicineListView(LoginRequiredMixin, ListView):
    """View for displaying all medicines in inventory"""
    model = Medicine
    template_name = 'medicines/medicine_list.html'  # This should match your template
    context_object_name = 'medicines'
    paginate_by = 12  # Display 12 medicines per page

    def get_queryset(self):
        """Custom queryset to allow filtering"""
        queryset = super().get_queryset()
        
        # Add filtering by category if provided in GET parameters
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Add search functionality if search term provided
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        """Add additional context data"""
        context = super().get_context_data(**kwargs)
        context['categories'] = MedicineCategory.objects.all()
        return context


class MedicineDetailView(LoginRequiredMixin, DetailView):
    """View for displaying details of a single medicine"""
    model = Medicine
    template_name = 'medicines/medicine_detail.html'
    context_object_name = 'medicine'


class MedicineCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new medicine"""
    model = Medicine
    template_name = 'medicines/medicine_form.html'
    fields = ['name', 'category', 'description', 'quantity_in_stock', 
              'unit_price', 'reorder_level', 'manufacturer', 
              'expiry_date', 'batch_number', 'image']
    success_url = reverse_lazy('medicines:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Medicine'
        context['button_text'] = 'Add Medicine'
        return context


class MedicineUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing medicine"""
    model = Medicine
    template_name = 'medicines/medicine_form.html'
    fields = ['name', 'category', 'description', 'quantity_in_stock', 
              'unit_price', 'reorder_level', 'manufacturer', 
              'expiry_date', 'batch_number', 'image']
    success_url = reverse_lazy('medicines-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Medicine'
        context['button_text'] = 'Update Medicine'
        return context


class MedicineDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a medicine"""
    model = Medicine
    template_name = 'medicines/medicine_confirm_delete.html'
    success_url = reverse_lazy('medicines-list')


# API endpoint for medicine details (for AJAX requests)
def medicine_detail_api(request, pk):
    """API endpoint for getting medicine details via AJAX"""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    data = {
        'id': medicine.pk,
        'name': medicine.name,
        'category': medicine.category.name if medicine.category else 'No Category',
        'description': medicine.description or 'No description available',
        'quantity_in_stock': medicine.quantity_in_stock,
        'reorder_level': medicine.reorder_level,
        'unit_price': str(medicine.unit_price),
        'manufacturer': medicine.manufacturer or 'Not specified',
        'batch_number': medicine.batch_number or 'Not specified',
        'expiry_date': medicine.expiry_date.strftime('%Y-%m-%d') if medicine.expiry_date else 'Not specified',
        'updated_at': medicine.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'image_url': medicine.image.url if medicine.image else None,
        'is_low_stock': medicine.is_low_stock
    }
    
    return JsonResponse(data)


# Category related views
class CategoryListView(LoginRequiredMixin, ListView):
    """View for displaying all medicine categories"""
    model = MedicineCategory
    template_name = 'medicines/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new medicine category"""
    model = MedicineCategory
    template_name = 'medicines/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('medicines:category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Category'
        context['button_text'] = 'Add Category'
        return context


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing medicine category"""
    model = MedicineCategory
    template_name = 'medicines/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('medicines-category-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Category'
        context['button_text'] = 'Update Category'
        return context


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a medicine category"""
    model = MedicineCategory
    template_name = 'medicines/category_confirm_delete.html'
    success_url = reverse_lazy('medicines-category-list')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import modelformset_factory, inlineformset_factory
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q

from .models import Patient, Appointment, Consultation, Prescription, Disease, Medicine
from .forms import PatientSearchForm, AppointmentForm, ConsultationForm, PrescriptionForm

@login_required
def patient_search_ajax(request):
    """AJAX endpoint for searching patients"""
    if request.method == 'GET':
        query = request.GET.get('q', '')
        if query:
            patients = Patient.objects.filter(
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query) | 
                Q(id_number__icontains=query)
            )[:10]  # Limit to 10 results
            results = []
            for patient in patients:
                results.append({
                    'id': patient.id,
                    'text': f"{patient.first_name} {patient.last_name} (ID: {patient.id_number})",
                    'dob': patient.date_of_birth.strftime('%Y-%m-%d'),
                    'gender': patient.get_gender_display(),
                    'phone': patient.phone_number
                })
            return JsonResponse({'results': results})
        return JsonResponse({'results': []})

from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def consultation_view(request):
    """
    Combined view for:
    - Searching patients
    - Creating/updating appointment
    - Adding consultation
    - Creating prescriptions
    All saved at once with a single form submission
    """
    patient_search_form = PatientSearchForm()
    appointment_form = AppointmentForm(initial={'doctor': request.user})
    consultation_form = ConsultationForm()
    
    # Create a formset for prescriptions - allow 5 empty forms initially
    PrescriptionFormSet = modelformset_factory(
        Prescription, 
        form=PrescriptionForm,
        extra=5, 
        can_delete=True
    )
    prescription_formset = PrescriptionFormSet(
        queryset=Prescription.objects.none(),
        prefix='prescriptions'
    )
    
    if request.method == 'POST':
        appointment_form = AppointmentForm(request.POST)
        consultation_form = ConsultationForm(request.POST)
        prescription_formset = PrescriptionFormSet(
            request.POST, 
            prefix='prescriptions'
        )
        
        if (appointment_form.is_valid() and 
            consultation_form.is_valid() and 
            prescription_formset.is_valid()):
            
            try:
                with transaction.atomic():
                    # Save appointment
                    appointment = appointment_form.save(commit=False)
                    appointment.status = 'IN_PROGRESS'
                    if hasattr(request.user, 'user_type') and request.user.user_type == 'RECEPTIONIST':
                        appointment.receptionist = request.user
                    appointment.save()
                    
                    # Save consultation
                    consultation = consultation_form.save(commit=False)
                    consultation.appointment = appointment
                    consultation.save()
                    
                    # Handle many-to-many field
                    consultation_form.save_m2m()
                    
                    # Save prescriptions
                    prescriptions = prescription_formset.save(commit=False)
                    for prescription in prescriptions:
                        if prescription.medicine_id:  # Only save if a medicine was selected
                            prescription.consultation = consultation
                            prescription.save()
                    
                    # Handle deleted prescriptions
                    for obj in prescription_formset.deleted_objects:
                        obj.delete()
                    
                    messages.success(request, f"Consultation for {appointment.patient} saved successfully.")
                    return redirect('consultation_detail', pk=consultation.pk)
            
            except Exception as e:
                messages.error(request, f"Error saving consultation: {str(e)}")
    
    context = {
        'patient_search_form': patient_search_form,
        'appointment_form': appointment_form,
        'consultation_form': consultation_form,
        'prescription_formset': prescription_formset,
        'medicines': Medicine.objects.all(),
        'diseases': Disease.objects.all(),
    }
    
    return render(request, 'clinic/consultation_form.html', context)


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .models import Consultation, Prescription

@login_required
def consultation_detail(request, pk):
    """
    View for displaying details of a specific consultation
    """
    # Get the consultation object or return 404
    consultation = get_object_or_404(Consultation, pk=pk)
    
    # Get the associated appointment
    appointment = consultation.appointment
    
    # Security check - only allow doctors, receptionists, or admin to view
    if hasattr(request.user, 'user_type'):
        is_allowed = (request.user.user_type in ['DOCTOR', 'RECEPTIONIST', 'ADMIN'] or 
                      request.user == appointment.doctor)
        if not is_allowed:
            return HttpResponseForbidden("You do not have permission to view this consultation")
    
    # Get all prescriptions for this consultation
    prescriptions = Prescription.objects.filter(consultation=consultation)
    
    context = {
        'consultation': consultation,
        'appointment': appointment,
        'patient': appointment.patient,
        'prescriptions': prescriptions,
    }
    
    return render(request, 'clinic/consultation_detail.html', context)




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Consultation

def consultation_list(request):
    # Search functionality
    search_query = request.GET.get('search', '')
    
    consultations = Consultation.objects.select_related(
        'appointment', 
        'appointment__patient', 
        'appointment__doctor'
    ).order_by('-created_at')
    
    if search_query:
        consultations = consultations.filter(
            Q(appointment__patient__first_name__icontains=search_query) |
            Q(appointment__patient__last_name__icontains=search_query) |
            Q(appointment__patient__id_number__icontains=search_query) |
            Q(diagnosis__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(consultations, 10)  # Show 10 consultations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'consultations/consultation_list.html', context)

def delete_consultation(request, pk):
    consultation = get_object_or_404(Consultation, pk=pk)
    
    if request.method == 'POST':
        # Check permissions (example - only doctors and admins can delete)
        if not (request.user.user_type in ['DOCTOR', 'ADMIN']):
            messages.error(request, "You don't have permission to delete consultations.")
            return redirect('consultation_list')
            
        consultation.delete()
        messages.success(request, "Consultation deleted successfully.")
        return redirect('consultation_list')
    
    return render(request, 'consultations/confirm_delete.html', {'consultation': consultation})


from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import MedicineSale, SoldMedicine
from datetime import datetime, timedelta

def medicine_sales_list(request):
    # Get filter parameters
    date_range = request.GET.get('date_range', 'today')
    search_query = request.GET.get('search', '')
    payment_method = request.GET.get('payment_method', '')
    
    # Base queryset
    sales = MedicineSale.objects.select_related(
        'patient', 
        'receptionist'
    ).prefetch_related('soldmedicine_set').order_by('-sale_date')
    
    # Apply date filters
    today = datetime.now().date()
    if date_range == 'today':
        sales = sales.filter(sale_date__date=today)
    elif date_range == 'week':
        start_date = today - timedelta(days=7)
        sales = sales.filter(sale_date__date__gte=start_date)
    elif date_range == 'month':
        start_date = today - timedelta(days=30)
        sales = sales.filter(sale_date__date__gte=start_date)
    elif date_range == 'year':
        start_date = today - timedelta(days=365)
        sales = sales.filter(sale_date__date__gte=start_date)
    
    # Apply payment method filter
    if payment_method:
        sales = sales.filter(payment_method=payment_method)
    
    # Apply search
    if search_query:
        sales = sales.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(patient__id_number__icontains=search_query) |
            Q(receptionist__first_name__icontains=search_query) |
            Q(receptionist__last_name__icontains=search_query) |
            Q(mpesa_code__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(sales, 15)  # 15 sales per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'date_range': date_range,
        'search_query': search_query,
        'payment_method': payment_method,
        'payment_methods': MedicineSale.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'medicine_sales/list.html', context)

def medicine_sale_detail(request, pk):
    sale = get_object_or_404(MedicineSale.objects.prefetch_related(
        'soldmedicine_set',
        'soldmedicine_set__medicine'
    ), pk=pk)
    
    sold_medicines = sale.soldmedicine_set.all()
    
    context = {
        'sale': sale,
        'sold_medicines': sold_medicines,
    }
    return render(request, 'medicine_sales/detail.html', context)



from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import PatientMedicalHistory, Patient

def all_medical_records(request):
    records = PatientMedicalHistory.objects.all().order_by('-date_recorded')
    
    # Pagination
    paginator = Paginator(records, 25)  # Show 25 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'records': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'medical_history/all_medical_records.html', context)

def patient_medical_history(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    medical_history = PatientMedicalHistory.objects.filter(patient=patient).order_by('-date_recorded')
    
    # Count different record types
    allergy_count = medical_history.filter(record_type='Allergy').count()
    chronic_condition_count = medical_history.filter(record_type='Chronic Condition').count()
    surgery_count = medical_history.filter(record_type='Surgery').count()
    
    # Filtered records for tabs
    allergies = medical_history.filter(record_type='Allergy')
    chronic_conditions = medical_history.filter(record_type='Chronic Condition')
    surgeries = medical_history.filter(record_type='Surgery')
    
    context = {
        'patient': patient,
        'medical_history': medical_history,
        'allergy_count': allergy_count,
        'chronic_condition_count': chronic_condition_count,
        'surgery_count': surgery_count,
        'allergies': allergies,
        'chronic_conditions': chronic_conditions,
        'surgeries': surgeries,
    }
    return render(request, 'medical_history/patient_medical_history.html', context)