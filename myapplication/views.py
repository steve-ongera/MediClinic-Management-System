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


from django.contrib.auth.decorators import login_required, user_passes_test
@login_required
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

    # Line chart sales data
    sales_data = MedicineSale.objects.filter(
        sale_date__gte=start_date
    ).annotate(
        date=Trunc('sale_date', 'day', output_field=DateTimeField())
    ).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')

    sales_dates = [item['date'].strftime('%Y-%m-%d') for item in sales_data]
    sales_amounts = [float(item['total']) for item in sales_data]

    # Payment method stats
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
            return redirect('patients:list')
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
    patient = get_object_or_404(Patient, pk=pk)
    
    # Calculate age
    today = datetime.date.today()
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