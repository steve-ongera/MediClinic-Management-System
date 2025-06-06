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
from django.contrib.auth.decorators import login_required
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
    
    # Total revenue from both MedicineSale and OverTheCounterSale
    medicine_sale_revenue = MedicineSale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    otc_sale_revenue = OverTheCounterSale.objects.filter(payment_status='completed').aggregate(total=Sum('total_amount'))['total'] or 0
    total_revenue = medicine_sale_revenue + otc_sale_revenue
   
    today = timezone.now().date()
    
    # Today's appointments
    todays_appointments = Appointment.objects.filter(
        scheduled_time__date=today
    ).order_by('scheduled_time')

    # Top 5 diseases
    common_diseases = Disease.objects.annotate(
        count=Count('consultation')
    ).order_by('-count')[:5]
    
    disease_labels = [d.name for d in common_diseases]
    disease_counts = [d.count for d in common_diseases]

    # Top 5 best-selling medicines
    # In your admin_dashboard_view
    # Top 5 best-selling medicines - with fallback for empty data
    best_selling = SoldMedicine.objects.values('medicine__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    # Ensure we always have 5 items for consistent chart display
    if len(best_selling) < 5:
        # Fill with empty data if needed
        for i in range(5 - len(best_selling)):
            best_selling.append({'medicine__name': f'Medicine {i+1}', 'total_sold': 0})

    medicine_labels = [item['medicine__name'] for item in best_selling]
    medicine_counts = [item['total_sold'] or 0 for item in best_selling]  # Ensure no None values

    # Line chart sales data - LAST 7 DAYS ONLY - Combined Medicine Sales and OTC Sales
    last_7_days = timezone.now() - timedelta(days=7)
    
    # Get MedicineSale data
    medicine_sales_data = MedicineSale.objects.filter(
        sale_date__gte=last_7_days
    ).annotate(
        date=Trunc('sale_date', 'day', output_field=DateTimeField())
    ).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')

    # Get OverTheCounterSale data
    otc_sales_data = OverTheCounterSale.objects.filter(
        created_at__gte=last_7_days,
        payment_status='completed'
    ).annotate(
        date=Trunc('created_at', 'day', output_field=DateTimeField())
    ).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')

    # Combine both sales data by date
    combined_sales = {}
    
    # Add medicine sales
    for item in medicine_sales_data:
        date_str = item['date'].strftime('%Y-%m-%d')
        combined_sales[date_str] = combined_sales.get(date_str, 0) + float(item['total'])
    
    # Add OTC sales
    for item in otc_sales_data:
        date_str = item['date'].strftime('%Y-%m-%d')
        combined_sales[date_str] = combined_sales.get(date_str, 0) + float(item['total'])

    # Sort by date and prepare for chart
    sales_dates = sorted(combined_sales.keys())
    sales_amounts = [combined_sales[date] for date in sales_dates]

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
    ).order_by('-scheduled_time')[:10]

    # Low stock medicines
    low_stock = Medicine.objects.filter(
        quantity_in_stock__lte=F('reorder_level')
    ).order_by('quantity_in_stock')[:5]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_medicines': total_medicines,
        'total_revenue': total_revenue,
        'todays_appointments': todays_appointments,
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


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Max

@login_required
def doctor_dashboard(request):
    if request.user.user_type != 'DOCTOR':
        raise PermissionDenied("Access denied. Only doctors can view this page.")

    doctor = request.user
    today = timezone.now().date()

    # Get today's appointments
    todays_appointments = Appointment.objects.filter(
        doctor=doctor,
        scheduled_time__date=today
    ).order_by('scheduled_time')

    # Get today's consultations
    todays_consultations = Consultation.objects.filter(
        appointment__doctor=doctor,
        created_at__date=today
    ).order_by('-created_at')

    # Get recent consultations (last 7 days)
    recent_consultations = Consultation.objects.filter(
        appointment__doctor=doctor,
        created_at__gte=today - timezone.timedelta(days=7)
    ).order_by('-created_at')[:6]

    # Get pending prescriptions (assuming you add a `status` field later)
    pending_prescriptions = Prescription.objects.filter(
        consultation__appointment__doctor=doctor,
        consultation__appointment__status='COMPLETED'  # optional filter
    )

    # Get pending approvals (optional, requires doctor.is_senior if used)
    pending_approvals = Prescription.objects.filter(
        consultation__appointment__doctor=doctor,
        consultation__appointment__status='COMPLETED',  # optional
        consultation__follow_up_notes__isnull=False     # example condition
    ) if getattr(doctor, 'is_senior', False) else Prescription.objects.none()

    # Get critical patients (assuming last_consultation exists and links to Consultation)
   # Get latest consultation per patient seen by this doctor
    latest_consults = Consultation.objects.filter(
        appointment__doctor=doctor
    ).values('appointment__patient').annotate(
        latest=Max('created_at')
    ).order_by('-latest')[:5]

    # Get patient IDs
    latest_patient_ids = [item['appointment__patient'] for item in latest_consults]

    # Get actual Patient objects
    critical_patients = Patient.objects.filter(id__in=latest_patient_ids)

    context = {
        'doctor': doctor,
        'todays_appointments': todays_appointments,
        'todays_consultations': todays_consultations,
        'recent_consultations': recent_consultations,
        'pending_prescriptions': pending_prescriptions,
        'pending_approvals': pending_approvals,
        'critical_patients': critical_patients,
    }

    return render(request, 'dashboard/doctor_dashboard.html', context)


# from django.core.exceptions import PermissionDenied
# @login_required
# def doctor_dashboard(request):

#     if request.user.user_type != 'DOCTOR':
#         raise PermissionDenied("Access denied. Only doctors can view this page.")
    
#     doctor = request.user  # Since your User model includes doctor info

#     today = timezone.now().date()
    
#     # Get today's appointments
#     todays_appointments = Appointment.objects.filter(
#         doctor=doctor,
#         scheduled_time__date=today
#     ).order_by('scheduled_time')
    
#     # Get today's consultations
#     todays_consultations = Consultation.objects.filter(
#         appointment__doctor=doctor,
#         created_at__date=today
#     ).order_by('-created_at')
    
#     # Get recent consultations (last 7 days)
#     recent_consultations = Consultation.objects.filter(
#         appointment__doctor=doctor,
#         created_at__gte=today-timezone.timedelta(days=7)
#     ).order_by('-created_at')[:6]
    
#     # Get pending prescriptions
#     pending_prescriptions = Prescription.objects.filter(
#         doctor=doctor,
#         status='PENDING'
#     )
    
#     # Get pending approvals (if doctor is a senior/approver)
#     Prescription.objects.filter(
#         consultation__appointment__doctor=doctor,
#         status='PENDING'
#     )

    
#     # Get critical patients
#     critical_patients = Patient.objects.filter(
#         is_critical=True,
#         last_consultation__doctor=doctor
#     )[:5]
    
#     # Get medical updates
#     # medical_updates = MedicalUpdate.objects.filter(
#     #     publish_date__lte=timezone.now()
#     # ).order_by('-publish_date')[:3]
    
#     context = {
#         'doctor': doctor,
#         'todays_appointments': todays_appointments,
#         'todays_consultations': todays_consultations,
#         'recent_consultations': recent_consultations,
#         'pending_prescriptions': pending_prescriptions,
#         'pending_approvals': pending_approvals,
#         'critical_patients': critical_patients,
#         #'medical_updates': medical_updates,
#     }
    
#     return render(request, 'dashboard/doctor_dashboard.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
import datetime
from .models import Patient
from .forms import PatientForm

@login_required
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


@login_required
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


@login_required
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

@login_required
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


@login_required
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


@login_required
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


@login_required
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

from django.http import JsonResponse, Http404
from .models import Medicine  # adjust as per your model import


@login_required
def get_medicine_detail(request, pk):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            medicine = Medicine.objects.select_related('category').get(pk=pk)
            data = {
                'name': medicine.name,
                'category': medicine.category.name if medicine.category else 'No category',
                'manufacturer': medicine.manufacturer,
                'batch_number': medicine.batch_number,
                'expiry_date': medicine.expiry_date.strftime('%Y-%m-%d') if medicine.expiry_date else '',
                'quantity_in_stock': medicine.quantity_in_stock,
                'reorder_level': medicine.reorder_level,
                'unit_price': str(medicine.unit_price),
                'last_updated': medicine.updated_at.strftime('%Y-%m-%d %H:%M:%S') if medicine.updated_at else '',
                'image_url': medicine.image.url if medicine.image else '',
            }
            return JsonResponse(data)
        except Medicine.DoesNotExist:
            raise Http404("Medicine not found")
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def update_medicine_ajax(request, pk):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            medicine = Medicine.objects.get(pk=pk)

            # Update fields
            medicine.name = data.get('name', medicine.name)
            medicine.price = data.get('price', medicine.price)
            medicine.description = data.get('description', medicine.description)
            medicine.save()

            return JsonResponse({'success': True, 'message': 'Medicine updated successfully.'})
        except Medicine.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Medicine not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request.'}, status=400)



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



@login_required
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


@login_required
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


@login_required
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

@login_required
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

@login_required
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


@login_required
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



from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Medicine
from django.db.models import Q



class MedicineStockListView(ListView):
    model = Medicine
    template_name = 'medicines/stock_list.html'
    context_object_name = 'medicines'
    paginate_by = 20

    def get_queryset(self):
        # Get all medicines ordered by stock status (lowest first)
        return Medicine.objects.all().order_by('quantity_in_stock')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Categorize medicines by stock level
        critical = Medicine.objects.filter(quantity_in_stock__lte=F('reorder_level')/2)
        warning = Medicine.objects.filter(
            quantity_in_stock__gt=F('reorder_level')/2,
            quantity_in_stock__lte=F('reorder_level')
        )
        sufficient = Medicine.objects.filter(quantity_in_stock__gt=F('reorder_level'))
        
        context.update({
            'critical_count': critical.count(),
            'warning_count': warning.count(),
            'sufficient_count': sufficient.count(),
        })
        return context

class MedicineDetailView(DetailView):
    model = Medicine
    template_name = 'medicines/detail.html'
    context_object_name = 'medicine'

def low_stock_medicines(request):
    # Get medicines below or at reorder level
    medicines = Medicine.objects.filter(
        quantity_in_stock__lte=F('reorder_level')
    ).order_by('quantity_in_stock')
    
    # Separate into critical (below half reorder) and warning (above half but below reorder)
    critical = medicines.filter(quantity_in_stock__lte=F('reorder_level')/2)
    warning = medicines.filter(quantity_in_stock__gt=F('reorder_level')/2)
    
    context = {
        'critical_medicines': critical,
        'warning_medicines': warning,
        'critical_count': critical.count(),
        'warning_count': warning.count(),
    }
    return render(request, 'medicines/low_stock.html', context)

from django.shortcuts import render, get_object_or_404
from .models import MedicineCategory, Medicine


@login_required
def medicine_category_list(request):
    categories = MedicineCategory.objects.all().order_by('name')
    
    # Count medicines in each category
    for category in categories:
        category.medicine_count = Medicine.objects.filter(category=category).count()
    
    context = {
        'categories': categories,
    }
    return render(request, 'medicines/category_list.html', context)


@login_required
def medicine_category_detail(request, category_id):
    category = get_object_or_404(MedicineCategory, pk=category_id)
    medicines = Medicine.objects.filter(category=category).order_by('name')
    
    # Stock status counts
    critical = medicines.filter(quantity_in_stock__lte=F('reorder_level')/2).count()
    warning = medicines.filter(
        quantity_in_stock__gt=F('reorder_level')/2,
        quantity_in_stock__lte=F('reorder_level')
    ).count()
    sufficient = medicines.filter(quantity_in_stock__gt=F('reorder_level')).count()
    
    context = {
        'category': category,
        'medicines': medicines,
        'critical_count': critical,
        'warning_count': warning,
        'sufficient_count': sufficient,
        'total_medicines': medicines.count(),
    }
    return render(request, 'medicines/category_detail.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Doctor
from .forms import DoctorForm  # You'll need to create this form


@login_required
def doctor_list(request):
    """
    Function-based view to display a list of all doctors with search and pagination.
    """
    search_query = request.GET.get('search', '')
    specialization_filter = request.GET.get('specialization', '')
    
    doctors = Doctor.objects.all()
    
    # Apply search filter
    if search_query:
        doctors = doctors.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(license_number__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Apply specialization filter
    if specialization_filter:
        doctors = doctors.filter(specialization=specialization_filter)
    
    # Order by last name
    doctors = doctors.order_by('last_name', 'first_name')
    
    # Pagination
    paginator = Paginator(doctors, 10)  # Show 10 doctors per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all specializations for filter dropdown
    specializations = Doctor.SPECIALIZATION_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'specialization_filter': specialization_filter,
        'specializations': specializations,
        'total_doctors': doctors.count(),
    }
    
    return render(request, 'doctors/doctor_list.html', context)



@login_required
def doctor_detail(request, pk):
    """
    Function-based view to display detailed information about a specific doctor.
    """
    doctor = get_object_or_404(Doctor, pk=pk)
    
    context = {
        'doctor': doctor,
    }
    
    return render(request, 'doctors/doctor_detail.html', context)



@login_required
def doctor_add(request):
    """
    Function-based view to add a new doctor.
    """
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f'Doctor {doctor.full_name} has been added successfully.')
            return redirect('doctor_detail', pk=doctor.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorForm()
    
    context = {
        'form': form,
        'title': 'Add New Doctor',
    }
    
    return render(request, 'doctors/doctor_form.html', context)



@login_required
def doctor_edit(request, pk):
    """
    Function-based view to edit an existing doctor.
    """
    doctor = get_object_or_404(Doctor, pk=pk)
    
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f'Doctor {doctor.full_name} has been updated successfully.')
            return redirect('doctor_detail', pk=doctor.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorForm(instance=doctor)
    
    context = {
        'form': form,
        'doctor': doctor,
        'title': f'Edit Doctor - {doctor.full_name}',
    }
    
    return render(request, 'doctors/doctor_form.html', context)



@login_required
def doctor_delete(request, pk):
    """
    Function-based view to delete a doctor (with confirmation).
    """
    doctor = get_object_or_404(Doctor, pk=pk)
    
    if request.method == 'POST':
        doctor_name = doctor.full_name
        doctor.delete()
        messages.success(request, f'Doctor {doctor_name} has been deleted successfully.')
        return redirect('doctor_list')
    
    context = {
        'doctor': doctor,
    }
    
    return render(request, 'doctors/doctor_confirm_delete.html', context)


from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json
from .models import MedicineSale, SoldMedicine, Medicine


@login_required
def financial_reports(request):
    # Time periods
    end_date = timezone.now()
    start_date_30d = end_date - timedelta(days=30)
    start_date_12m = end_date - timedelta(days=365)
    
    # 1. Revenue by Day (last 30 days)
    daily_sales = MedicineSale.objects.filter(
        sale_date__gte=start_date_30d
    ).extra({
        'date': "date(sale_date)"
    }).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')
    
    days = [item['date'] for item in daily_sales]
    daily_revenue = [float(item['total']) for item in daily_sales]
    
    # 2. Revenue by Month (last 12 months) - Fixed SQLite version
    monthly_sales = MedicineSale.objects.filter(
        sale_date__gte=start_date_12m
    ).extra({
        'month': "strftime('%%Y-%%m', sale_date)"
    }).values('month').annotate(
        total=Sum('total_amount')
    ).order_by('month')
    
    months = [item['month'] for item in monthly_sales]
    monthly_revenue = [float(item['total']) for item in monthly_sales]
    
    # 3. Payment Method Distribution
    payment_methods = MedicineSale.objects.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('-total')
    
    payment_labels = [item['payment_method'] for item in payment_methods]
    payment_counts = [item['count'] for item in payment_methods]
    payment_amounts = [float(item['total']) for item in payment_methods]
    
    # 4. Top Selling Medicines (for table)
    top_medicines = SoldMedicine.objects.values(
        'medicine__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('unit_price')
    ).order_by('-total_revenue')[:10]
    
    # 5. Financial Summary
    total_revenue = MedicineSale.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_sales = MedicineSale.objects.count()
    avg_sale_value = total_revenue / total_sales if total_sales > 0 else 0
    
    context = {
        'days': json.dumps(days),
        'daily_revenue': json.dumps(daily_revenue),
        'months': json.dumps(months),
        'monthly_revenue': json.dumps(monthly_revenue),
        'payment_labels': json.dumps(payment_labels),
        'payment_counts': json.dumps(payment_counts),
        'payment_amounts': json.dumps(payment_amounts),
        'top_medicines': top_medicines,
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'avg_sale_value': avg_sale_value,
    }
    
    return render(request, 'reports/financial_reports.html', context)



from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import Consultation, Disease


@login_required
def clinical_reports(request):
    # Date ranges
    end_date = timezone.now().date()
    start_date_30days = end_date - timedelta(days=30)
    start_date_12months = end_date - timedelta(days=365)
    
    # Top diseases - last 30 days
    recent_consultations = Consultation.objects.filter(
        created_at__date__gte=start_date_30days
    )
    
    top_diseases_30days = (
        Disease.objects.filter(consultation__in=recent_consultations)
        .annotate(count=Count('consultation'))
        .order_by('-count')[:10]
    )
    
    # Monthly disease trends - last 12 months
    monthly_disease_data = (
        Consultation.objects.filter(created_at__date__gte=start_date_12months)
        .values('diseases__name', month=models.functions.TruncMonth('created_at'))
        .annotate(count=Count('diseases'))
        .order_by('month', 'diseases__name')
    )
    
    # Prepare data for charts
    diseases_30days_labels = [d.name for d in top_diseases_30days]
    diseases_30days_counts = [d.count for d in top_diseases_30days]
    
    # Prepare monthly data
    monthly_labels = []
    monthly_datasets = {}
    
    for entry in monthly_disease_data:
        month = entry['month'].strftime("%b %Y")
        disease = entry['diseases__name']
        count = entry['count']
        
        if month not in monthly_labels:
            monthly_labels.append(month)
        
        if disease not in monthly_datasets:
            monthly_datasets[disease] = {
                'label': disease,
                'data': [],
                'borderColor': get_random_color(),
                'backgroundColor': get_random_color(0.2),
                'borderWidth': 2
            }
        
        monthly_datasets[disease]['data'].append(count)
    
    # Fill in missing months with 0 for each disease
    for disease in monthly_datasets.values():
        if len(disease['data']) < len(monthly_labels):
            disease['data'] = [0] * (len(monthly_labels) - len(disease['data'])) + disease['data']
    
    context = {
        'top_diseases_30days': zip(diseases_30days_labels, diseases_30days_counts),
        'diseases_30days_labels': diseases_30days_labels,
        'diseases_30days_counts': diseases_30days_counts,
        'monthly_labels': monthly_labels,
        'monthly_datasets': list(monthly_datasets.values()),
        'report_date': end_date.strftime("%B %d, %Y"),
        'start_date_30days': start_date_30days.strftime("%B %d, %Y"),
        'start_date_12months': start_date_12months.strftime("%B %Y"),
    }
    
    return render(request, 'reports/clinical_reports.html', context)

def get_random_color(opacity=1):
    import random
    colors = [
        f'rgba(54, 162, 235, {opacity})',  # Blue
        f'rgba(255, 99, 132, {opacity})',   # Red
        f'rgba(75, 192, 192, {opacity})',    # Teal
        f'rgba(255, 159, 64, {opacity})',    # Orange
        f'rgba(153, 102, 255, {opacity})',   # Purple
        f'rgba(255, 205, 86, {opacity})',    # Yellow
        f'rgba(201, 203, 207, {opacity})',   # Gray
        f'rgba(0, 128, 0, {opacity})',       # Green
        f'rgba(128, 0, 0, {opacity})',       # Maroon
        f'rgba(0, 0, 128, {opacity})',       # Navy
    ]
    return random.choice(colors)



from django.shortcuts import render
from django.db.models import Sum, F, ExpressionWrapper, FloatField, Count
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
import json
from .models import Medicine, MedicineCategory, SoldMedicine


@login_required
def inventory_reports(request):
    # Current inventory status
    inventory_status = Medicine.objects.annotate(
        total_value=ExpressionWrapper(
            F('quantity_in_stock') * F('unit_price'),
            output_field=FloatField()
        )
    ).order_by('quantity_in_stock')
    
    # Low stock items (below reorder level)
    low_stock_items = Medicine.objects.filter(
        quantity_in_stock__lte=F('reorder_level')
    ).order_by('quantity_in_stock')
    
    # Expired or soon-to-expire medicines
    soon_to_expire = Medicine.objects.filter(
        expiry_date__gte=timezone.now().date(),
        expiry_date__lte=timezone.now().date() + timedelta(days=30)
    ).order_by('expiry_date')
    
    expired_items = Medicine.objects.filter(
        expiry_date__lt=timezone.now().date()
    ).order_by('expiry_date')
    
    # Sales data - last 30 days
    start_date = timezone.now().date() - timedelta(days=30)
    top_selling = (
        SoldMedicine.objects.filter(sale__sale_date__gte=start_date)
        .values('medicine__name', 'medicine__category__name')
        .annotate(
            total_sold=Coalesce(Sum('quantity'), 0),
            total_revenue=ExpressionWrapper(
                Coalesce(Sum(F('quantity') * F('unit_price')), 0),
                output_field=FloatField()
            )
        )
        .order_by('-total_sold')[:10]
    )
    
    # Category breakdown
    categories = MedicineCategory.objects.annotate(
        item_count=Count('medicine'),
        total_quantity=Coalesce(Sum('medicine__quantity_in_stock'), 0),
        total_value=ExpressionWrapper(
            Coalesce(Sum(F('medicine__quantity_in_stock') * F('medicine__unit_price')), 0),
            output_field=FloatField()
        )
    )
    
    # Prepare chart data
    categories_labels = [c.name for c in categories]
    categories_quantities = [c.total_quantity for c in categories]
    categories_values = [float(c.total_value) for c in categories]
    
    top_selling_labels = [item['medicine__name'] for item in top_selling]
    top_selling_quantities = [item['total_sold'] for item in top_selling]
    
    # Calculate total inventory value safely
    total_inventory_value = float(
        Medicine.objects.aggregate(
            total=ExpressionWrapper(
                Coalesce(Sum(F('quantity_in_stock') * F('unit_price')), 0),
                output_field=FloatField()
            )
        )['total'] or 0
    )
    
    context = {
        'inventory_status': inventory_status,
        'low_stock_items': low_stock_items,
        'soon_to_expire': soon_to_expire,
        'expired_items': expired_items,
        'top_selling': top_selling,
        'categories': categories,
        'categories_labels': json.dumps(categories_labels),
        'categories_quantities': json.dumps(categories_quantities),
        'categories_values': json.dumps(categories_values),
        'top_selling_labels': json.dumps(top_selling_labels),
        'top_selling_quantities': json.dumps(top_selling_quantities),
        'report_date': timezone.now().strftime("%B %d, %Y"),
        'start_date': start_date.strftime("%B %d, %Y"),
        'total_inventory_value': total_inventory_value,
    }
    
    return render(request, 'reports/inventory_reports.html', context)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from .models import User
from .forms import UserForm, UserEditForm

@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_management(request):
    # Search functionality
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    user_type_filter = request.GET.get('user_type', '')
    
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if status_filter:
        users = users.filter(is_active=status_filter == 'active')
    
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)
    
    # Sort by last name
    users = users.order_by('last_name', 'first_name')
    
    context = {
        'users': users,
        'search_query': search_query,
        'status_filter': status_filter,
        'user_type_filter': user_type_filter,
        'user_types': User.USER_TYPE_CHOICES,
        'now': timezone.now(),
    }
    
    return render(request, 'user_management/user_list.html', context)

@login_required
@permission_required('auth.add_user', raise_exception=True)
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('user_management')
    else:
        form = UserForm()
    
    return render(request, 'user_management/user_form.html', {
        'form': form,
        'title': 'Create New User'
    })

@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('user_management')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'user_management/user_form.html', {
        'form': form,
        'title': f'Edit User: {user.username}',
        'user': user
    })

@login_required
@permission_required('auth.delete_user', raise_exception=True)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('user_management')
    
    return render(request, 'user_management/user_confirm_delete.html', {
        'user': user
    })

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta, date
import calendar
from .models import Doctor, Appointment, DoctorSchedule, DoctorLeave, WorkloadSummary


@login_required
def doctor_calendar_view(request):
    """Main calendar view for doctors"""
    # Get all doctors for the filter dropdown
    doctors = Doctor.objects.filter(is_active=True)
    
    # Get selected doctor (default to first doctor or logged-in doctor)
    selected_doctor_id = request.GET.get('doctor_id')
    if selected_doctor_id:
        selected_doctor = get_object_or_404(Doctor, id=selected_doctor_id)
    else:
        # If user is a doctor, show their calendar, otherwise show first doctor
        try:
            selected_doctor = request.user.doctor
        except:
            selected_doctor = doctors.first() if doctors.exists() else None
    
    # Get selected month and year
    current_date = timezone.now().date()
    selected_month = int(request.GET.get('month', current_date.month))
    selected_year = int(request.GET.get('year', current_date.year))
    
    # Generate calendar data
    calendar_data = generate_calendar_data(selected_doctor, selected_year, selected_month)
    
    context = {
        'doctors': doctors,
        'selected_doctor': selected_doctor,
        'calendar_data': calendar_data,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_name': calendar.month_name[selected_month],
        'current_date': current_date,
        'prev_month': get_prev_month(selected_year, selected_month),
        'next_month': get_next_month(selected_year, selected_month),
    }
    
    return render(request, 'calendar/doctor_calendar.html', context)

def generate_calendar_data(doctor, year, month):
    """Generate calendar data with workload information"""
    if not doctor:
        return []
    
    # Get first and last day of the month
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # Get all appointments for the doctor in this month
    appointments = Appointment.objects.filter(
        doctor=doctor.user,  # Use doctor.user instead of doctor
        scheduled_time__date__range=[first_day, last_day]
    ).select_related('patient')
    
    # Get doctor's leaves
    leaves = DoctorLeave.objects.filter(
        doctor=doctor,
        start_date__lte=last_day,
        end_date__gte=first_day,
        approved=True
    )
    
    # Generate calendar days
    cal = calendar.monthcalendar(year, month)
    calendar_weeks = []
    
    for week in cal:
        calendar_week = []
        for day in week:
            if day == 0:
                calendar_week.append(None)
            else:
                day_date = date(year, month, day)
                
                # Get appointments for this day
                day_appointments = [apt for apt in appointments if apt.scheduled_time.date() == day_date]
                
                # Check if doctor is on leave
                is_on_leave = any(leave.start_date <= day_date <= leave.end_date for leave in leaves)
                
                # Calculate workload
                workload_info = calculate_day_workload(doctor, day_date, day_appointments)
                
                day_data = {
                    'day': day,
                    'date': day_date,
                    'appointments': day_appointments,
                    'appointment_count': len(day_appointments),
                    'is_on_leave': is_on_leave,
                    'workload_percentage': workload_info['workload_percentage'],
                    'workload_level': workload_info['workload_level'],
                    'total_hours': workload_info['total_hours'],
                    'is_today': day_date == timezone.now().date(),
                    'is_weekend': day_date.weekday() >= 5,
                }
                calendar_week.append(day_data)
        calendar_weeks.append(calendar_week)
    
    return calendar_weeks

def calculate_day_workload(doctor, day_date, appointments):
    """Calculate workload for a specific day"""
    # Get doctor's schedule for this day
    day_of_week = day_date.weekday()
    schedules = DoctorSchedule.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week,
        is_active=True
    )
    
    if not schedules.exists():
        return {
            'workload_percentage': 0,
            'workload_level': 'none',
            'total_hours': 0
        }
    
    # Calculate total scheduled hours
    total_scheduled_minutes = 0
    max_patients = 0
    for schedule in schedules:
        # Convert times to minutes for calculation
        start_minutes = schedule.start_time.hour * 60 + schedule.start_time.minute
        end_minutes = schedule.end_time.hour * 60 + schedule.end_time.minute
        total_scheduled_minutes += (end_minutes - start_minutes)
        max_patients += schedule.max_patients
    
    # Calculate actual workload
    total_appointment_minutes = sum(apt.duration for apt in appointments)
    
    # Calculate workload percentage
    if total_scheduled_minutes > 0:
        workload_percentage = min(100, (total_appointment_minutes / total_scheduled_minutes) * 100)
    else:
        workload_percentage = 0
    
    # Determine workload level
    if workload_percentage == 0:
        workload_level = 'none'
    elif workload_percentage <= 25:
        workload_level = 'light'
    elif workload_percentage <= 50:
        workload_level = 'moderate'
    elif workload_percentage <= 75:
        workload_level = 'heavy'
    else:
        workload_level = 'overloaded'
    
    return {
        'workload_percentage': round(workload_percentage, 1),
        'workload_level': workload_level,
        'total_hours': round(total_scheduled_minutes / 60, 1)
    }

def get_prev_month(year, month):
    """Get previous month and year"""
    if month == 1:
        return {'year': year - 1, 'month': 12}
    return {'year': year, 'month': month - 1}

def get_next_month(year, month):
    """Get next month and year"""
    if month == 12:
        return {'year': year + 1, 'month': 1}
    return {'year': year, 'month': month + 1}

def doctor_day_detail_ajax(request, doctor_id, date_str):
    """Ajax view to get detailed information for a specific day"""
    try:
        doctor = get_object_or_404(Doctor, id=doctor_id)
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get appointments for the day
        appointments = Appointment.objects.filter(
            doctor=doctor,
            scheduled_time__date=selected_date
        ).select_related('patient').order_by('scheduled_time')
        
        # Get doctor's schedule for this day
        day_of_week = selected_date.weekday()
        schedules = DoctorSchedule.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True
        )
        
        # Check if doctor is on leave
        is_on_leave = DoctorLeave.objects.filter(
            doctor=doctor,
            start_date__lte=selected_date,
            end_date__gte=selected_date,
            approved=True
        ).exists()
        
        # Prepare appointment data
        appointment_data = []
        for apt in appointments:
            appointment_data.append({
                'id': apt.id,
                'patient_name': f"{apt.patient.first_name} {apt.patient.last_name}",
                'time': apt.scheduled_time.strftime('%H:%M'),
                'duration': apt.duration,
                'type': apt.get_appointment_type_display(),
                'status': apt.get_status_display(),
                'reason': apt.reason,
                'end_time': (apt.scheduled_time + timedelta(minutes=apt.duration)).strftime('%H:%M'),
            })
        
        # Prepare schedule data
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'max_patients': schedule.max_patients,
            })
        
        # Calculate workload
        workload_info = calculate_day_workload(doctor, selected_date, appointments)
        
        return JsonResponse({
            'success': True,
            'date': selected_date.strftime('%Y-%m-%d'),
            'doctor_name': str(doctor),
            'appointments': appointment_data,
            'schedules': schedule_data,
            'is_on_leave': is_on_leave,
            'workload_info': workload_info,
            'appointment_count': len(appointments),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def doctor_workload_analytics(request):
    """View for workload analytics and reports"""
    # Get all doctors
    doctors = Doctor.objects.filter(is_active=True)
    
    # Get date range (default to current month)
    current_date = timezone.now().date()
    start_date = request.GET.get('start_date', current_date.replace(day=1))
    end_date = request.GET.get('end_date', current_date)
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Generate analytics data
    analytics_data = []
    for doctor in doctors:
        # Get appointments in date range
        appointments = Appointment.objects.filter(
            doctor=doctor,
            scheduled_time__date__range=[start_date, end_date]
        )
        
        # Calculate metrics
        total_appointments = appointments.count()
        completed_appointments = appointments.filter(status='completed').count()
        avg_daily_appointments = total_appointments / max(1, (end_date - start_date).days + 1)
        
        # Get busiest day
        busiest_day_data = appointments.extra(
            select={'day': 'date(scheduled_time)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        analytics_data.append({
            'doctor': doctor,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'avg_daily_appointments': round(avg_daily_appointments, 1),
            'busiest_day': busiest_day_data['day'] if busiest_day_data else None,
            'busiest_day_count': busiest_day_data['count'] if busiest_day_data else 0,
        })
    
    context = {
        'doctors': doctors,
        'analytics_data': analytics_data,
        'start_date': start_date,
        'end_date': end_date,
        'date_range_days': (end_date - start_date).days + 1,
    }
    
    return render(request, 'calendar/workload_analytics.html', context)


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Appointment

@login_required
def appointment_list(request):
    """View to list appointments with search and pagination"""
    # Get query parameters
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    page = request.GET.get('page', 1)
    
    # Get appointments, ordered by the latest first
    appointments = Appointment.objects.all().order_by('-scheduled_time')
    
    # Apply filters
    if search_query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(doctor__first_name__icontains=search_query) |
            Q(doctor__last_name__icontains=search_query) |
            Q(reason__icontains=search_query)
        )
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        try:
            # Filter by selected date
            filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments = appointments.filter(scheduled_time__date=filter_date)
        except ValueError:
            pass  # Invalid date format, ignore the filter
    
    # Pagination
    paginator = Paginator(appointments, 10)  # 10 appointments per page
    
    try:
        appointments_page = paginator.page(page)
    except PageNotAnInteger:
        appointments_page = paginator.page(1)
    except EmptyPage:
        appointments_page = paginator.page(paginator.num_pages)
    
    # Get status choices for filter dropdown
    status_choices = Appointment.STATUS_CHOICES
    
    context = {
        'appointments': appointments_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': status_choices,
        'today': timezone.now().date(),
    }
    
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def appointment_detail_ajax(request, appointment_id):
    """AJAX view to get appointment details for modal"""
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Format data for JSON response
        appointment_data = {
            'id': appointment.id,
            'patient_name': f"{appointment.patient.first_name} {appointment.patient.last_name}",
            'patient_id': appointment.patient.id,
            'doctor_name': f"Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}",
            'doctor_id': appointment.doctor.id,
            'scheduled_time': appointment.scheduled_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': appointment.end_time.strftime('%Y-%m-%d %H:%M') if appointment.end_time else 'Not set',
            'status': appointment.get_status_display(),
            'reason': appointment.reason,
            'symptoms': appointment.symptoms or 'None recorded',
            'created_at': appointment.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': appointment.updated_at.strftime('%Y-%m-%d %H:%M'),
            'receptionist_name': f"{appointment.receptionist.first_name} {appointment.receptionist.last_name}" if appointment.receptionist else 'N/A',
        }
        
        return JsonResponse({
            'success': True,
            'appointment': appointment_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
    


@login_required
def help_support(request):
    return render(request, 'help_support.html')


@login_required
def user_manual(request):
    return render(request, 'user-manual.html')



from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse

# Custom template tag for splitting strings
from django import template
register = template.Library()

@register.filter
def split(value, arg):
    """Split a string into a list on the given delimiter"""
    return value.split(arg)


# Helper function to check if user is admin/staff
def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def clinic_settings(request):
    """
    View for clinic system settings page
    Only accessible by staff/admin users
    """
    if request.method == 'POST':
        # Process the submitted form data
        try:
            # Extract form data
            clinic_name = request.POST.get('clinicName')
            timezone = request.POST.get('timezone')
            currency = request.POST.get('currency')
            date_format = request.POST.get('dateFormat')
            
            # Working hours processing
            working_hours = {}
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                is_active = request.POST.get(f'{day}Toggle') == 'on'
                open_time = request.POST.get(f'{day}Open')
                close_time = request.POST.get(f'{day}Close')
                working_hours[day] = {
                    'active': is_active,
                    'open': open_time,
                    'close': close_time
                }
            
            # Appointment settings
            slot_duration = int(request.POST.get('slotDuration'))
            max_patients = int(request.POST.get('maxPatients'))
            booking_days = int(request.POST.get('bookingDays'))
            cancel_hours = int(request.POST.get('cancelHours'))
            
            # Security settings
            session_timeout = int(request.POST.get('sessionTimeout'))
            require_upper = request.POST.get('requireUpper') == 'on'
            require_special = request.POST.get('requireSpecial') == 'on'
            require_digit = request.POST.get('requireDigit') == 'on'
            min_password_length = int(request.POST.get('minPasswordLength'))
            
            # TODO: Save settings to your settings model or configuration
            # settings = ClinicSettings.objects.first()
            # settings.clinic_name = clinic_name
            # ...
            # settings.save()
            
            messages.success(request, "Settings updated successfully")
            return HttpResponseRedirect(reverse('system_settings'))
        
        except Exception as e:
            messages.error(request, f"Error updating settings: {str(e)}")
            return HttpResponseRedirect(reverse('system_settings'))
    
    # For GET requests, load current settings
    # You would typically load these from your database
    context = {
        'current_settings': {
            'clinic_name': 'Harmony Medical Clinic',
            'clinic_logo': '/static/assets/img/clinic-logo.png',
            'timezone': 'America/New_York',
            'currency': 'USD',
            'date_format': 'MM/DD/YYYY',
        },
        'working_hours': {
            'monday': {'active': True, 'open': '08:00', 'close': '18:00'},
            'tuesday': {'active': True, 'open': '08:00', 'close': '18:00'},
            'wednesday': {'active': True, 'open': '08:00', 'close': '18:00'},
            'thursday': {'active': True, 'open': '08:00', 'close': '18:00'},
            'friday': {'active': True, 'open': '08:00', 'close': '18:00'},
            'saturday': {'active': True, 'open': '09:00', 'close': '14:00'},
            'sunday': {'active': False, 'open': '', 'close': ''},
        },
        'appointment_settings': {
            'slot_duration': 30,
            'max_patients': 50,
            'booking_days': 30,
            'cancel_hours': 24,
        },
        'security_settings': {
            'session_timeout': 60,
            'require_upper': True,
            'require_special': True,
            'require_digit': True,
            'min_password_length': 8,
        },
        'days_of_week': 'Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday',
    }
    
    # Add any system messages you want to display
    if not request.session.get('settings_viewed'):
        messages.info(request, "You can customize your clinic settings here")
        request.session['settings_viewed'] = True
        
    return render(request, 'clinic-settings.html', context)





def custom_page_not_found(request, exception):
    return render(request, '404.html', status=404)

def custom_server_error(request):
    return render(request, '500.html', status=500)

from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.cache import cache
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
Account = get_user_model()

#forgot password view 
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)

            # Generate reset password token and send email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            context = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http'
            }
            
            # Render both HTML and plain text versions of the email
            html_message = render_to_string('auth/reset_password_email.html', context)
            plain_message = strip_tags(html_message)
            
            to_email = email
            
            # Use EmailMultiAlternatives for sending both HTML and plain text
            email = EmailMultiAlternatives(
                mail_subject,
                plain_message,
                'noreply@yourdomain.com',
                [to_email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgot_password')
    return render(request, 'auth/forgot_password.html')



def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                if len(password) < 6:
                    messages.error(request, 'Password must be at least 6 characters.')
                    return redirect('reset_password', uidb64=uidb64, token=token)

                user.set_password(password)
                user.last_password_change = timezone.now()
                user.save()
                messages.success(request, 'Password reset successful. You can now login with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect('reset_password', uidb64=uidb64, token=token)

        # GET request – render the form
        return render(request, 'auth/reset_password.html')
    else:
        messages.error(request, 'Invalid or expired reset link. Please try again.')
        return redirect('login')
    


from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta, datetime

from .models import (
    User, Patient, Appointment, Doctor, Consultation, 
    Prescription, Medicine, MedicineSale
)

def is_receptionist(user):
    return user.is_authenticated and user.user_type == 'RECEPTIONIST'

@login_required
@user_passes_test(is_receptionist)
def receptionist_dashboard(request):
    # Get current date and time
    today = timezone.now().date()
    one_week_ago = today - timedelta(days=7)
    
    # Today's appointments
    todays_appointments = Appointment.objects.filter(
        scheduled_time__date=today
    ).order_by('scheduled_time')
    
    # New patients registered this week
    new_patients_this_week = Patient.objects.filter(
        created_at__gte=one_week_ago
    ).count()
    
    # Recent patient registrations (last 6)
    recent_patients = Patient.objects.order_by('-created_at')[:6]
    
    # Add age property to patients (since it's defined in the model as a property)
    for patient in recent_patients:
        # Ensure patients have a full_name attribute
        patient.full_name = f"{patient.first_name} {patient.last_name}"
    
    # Available doctors for today
    # This assumes doctors with schedules for today are available
    available_doctors = Doctor.objects.filter(
        is_active=True,
        doctorschedule__day_of_week=today.weekday(),
        doctorschedule__is_active=True
    ).distinct()
    
    # Make sure Doctor objects have the needed attributes
    for doctor in available_doctors:
        if not hasattr(doctor, 'working_hours') or not doctor.working_hours:
            # Get schedule for today
            schedule = doctor.doctorschedule_set.filter(
                day_of_week=today.weekday(),
                is_active=True
            ).first()
            if schedule:
                doctor.working_hours = f"{schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')}"
            else:
                doctor.working_hours = "Not specified"
    
    # Pending prescriptions (not yet filled/sold)
    # This is an approximation as we don't have a specific field for "filled" status
    recent_consultations = Consultation.objects.filter(
        created_at__gte=one_week_ago
    )
    pending_prescriptions = Prescription.objects.filter(
        consultation__in=recent_consultations
    )
    
    # Sample announcements (would come from a real model in production)
    announcements = [
        {
            'title': 'Staff Meeting',
            'content': 'Reminder: Monthly staff meeting on Friday at 4:00 PM.',
            'created_at': datetime.now() - timedelta(hours=3),
            'is_new': True
        },
        {
            'title': 'New COVID Protocol',
            'content': 'Updated COVID safety protocols are now in effect. Please review the guidelines.',
            'created_at': datetime.now() - timedelta(days=2),
            'is_new': False
        },
        {
            'title': 'System Maintenance',
            'content': 'System will be down for maintenance on Sunday from 2 AM to 5 AM.',
            'created_at': datetime.now() - timedelta(days=4),
            'is_new': False
        }
    ]
    
    context = {
        'todays_appointments': todays_appointments,
        'new_patients_this_week': new_patients_this_week,
        'recent_patients': recent_patients,
        'available_doctors': available_doctors,
        'pending_prescriptions': pending_prescriptions,
        'announcements': announcements,
    }
    
    return render(request, 'dashboard/receptionist_dashboard.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import View
from django.db import transaction
from .models import Consultation, Prescription, MedicineSale, SoldMedicine
from .forms import MedicineSaleForm
import logging

# Set up logging
logger = logging.getLogger(__name__)

class CreateMedicineSaleFromConsultation(View):
    template_name = 'pharmacy/create_sale_from_consultation.html'
    
    def get(self, request, *args, **kwargs):
        form = MedicineSaleForm()
        consultation_code = request.GET.get('consultation_code', '')
        prescriptions = []
        total_amount = 0
        consultation = None
        patient = None
        
        if consultation_code:
            try:
                consultation = Consultation.objects.select_related(
                    'appointment', 'appointment__patient'
                ).get(consultation_code=consultation_code)
                
                prescriptions = Prescription.objects.filter(consultation=consultation)
                patient = consultation.appointment.patient
                
                if not prescriptions.exists():
                    messages.warning(request, 'No prescriptions found for this consultation')
                else:
                    # Calculate total amount
                    total_amount = sum(
                        prescription.quantity * prescription.medicine.unit_price 
                        for prescription in prescriptions
                    )
                    
                    # Initialize form with patient data
                    form = MedicineSaleForm(initial={
                        'patient': patient.id,
                        'receptionist': request.user.id,
                    })
                
            except Consultation.DoesNotExist:
                messages.error(request, 'Consultation with this code does not exist')
            except Exception as e:
                logger.error(f"Error in get method: {str(e)}")
                messages.error(request, f'An error occurred: {str(e)}')
        
        context = {
            'form': form,
            'consultation_code': consultation_code,
            'prescriptions': prescriptions,
            'total_amount': total_amount,
            'consultation': consultation,
            'patient': patient,
        }
        return render(request, self.template_name, context)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = MedicineSaleForm(request.POST)
        consultation_code = request.POST.get('consultation_code', '')
        prescriptions = []
        patient = None
        
        # Check if consultation code is provided
        if not consultation_code:
            messages.error(request, 'Consultation code is required')
            return redirect('create_sale_from_consultation')
        
        try:
            # Get consultation and related data
            consultation = Consultation.objects.select_related(
                'appointment', 'appointment__patient'
            ).get(consultation_code=consultation_code)
            
            prescriptions = list(Prescription.objects.select_related('medicine').filter(consultation=consultation))
            patient = consultation.appointment.patient
            
            if not prescriptions:
                messages.error(request, 'No prescriptions found for this consultation')
                context = {
                    'form': form,
                    'consultation_code': consultation_code,
                    'consultation': consultation,
                    'patient': patient,
                }
                return render(request, self.template_name, context)
            
            # Calculate total amount
            total_amount = sum(
                prescription.quantity * prescription.medicine.unit_price 
                for prescription in prescriptions
            )
            
            # Check for sufficient stock before proceeding
            insufficient_stock = []
            for prescription in prescriptions:
                if prescription.medicine.quantity_in_stock < prescription.quantity:
                    insufficient_stock.append(
                        f"{prescription.medicine.name} (needed: {prescription.quantity}, available: {prescription.medicine.quantity_in_stock})"
                    )
            
            if insufficient_stock:
                error_msg = "Insufficient stock for: " + ", ".join(insufficient_stock)
                messages.error(request, error_msg)
                context = {
                    'form': form,
                    'consultation_code': consultation_code,
                    'prescriptions': prescriptions,
                    'total_amount': total_amount,
                    'consultation': consultation,
                    'patient': patient,
                }
                return render(request, self.template_name, context)
            
            # Process the form
            if form.is_valid():
                logger.info(f"Form is valid: {form.cleaned_data}")
                try:
                    # Create the MedicineSale
                    medicine_sale = form.save(commit=False)
                    medicine_sale.patient = patient
                    medicine_sale.total_amount = total_amount
                    medicine_sale.save()
                    logger.info(f"Medicine sale created with ID: {medicine_sale.id}")
                    
                    # Create SoldMedicine records for each prescription and update stock
                    for prescription in prescriptions:
                        sold_medicine = SoldMedicine.objects.create(
                            sale=medicine_sale,
                            medicine=prescription.medicine,
                            quantity=prescription.quantity,
                            unit_price=prescription.medicine.unit_price
                        )
                        logger.info(f"Created SoldMedicine: {sold_medicine.id} for {prescription.medicine.name}")
                        
                        # Update medicine stock with select_for_update for thread safety
                        medicine = Medicine.objects.select_for_update().get(pk=prescription.medicine.pk)
                        
                        # Double-check stock availability (in case of concurrent sales)
                        if medicine.quantity_in_stock >= prescription.quantity:
                            medicine.quantity_in_stock -= prescription.quantity
                            medicine.save(update_fields=['quantity_in_stock'])
                            logger.info(f"Updated stock for {medicine.name}: new stock = {medicine.quantity_in_stock}")
                        else:
                            # If stock became insufficient due to concurrent sales, rollback
                            raise ValueError(f"Insufficient stock for {medicine.name}. Available: {medicine.quantity_in_stock}, Required: {prescription.quantity}")
                    
                    messages.success(request, f'Medicine sale #{medicine_sale.id} created successfully')
                    return redirect('medicine_sale_detail', pk=medicine_sale.id)
                    
                except ValueError as ve:
                    logger.error(f"Stock validation error: {str(ve)}")
                    messages.error(request, str(ve))
                    # Re-render form with context
                    context = {
                        'form': form,
                        'consultation_code': consultation_code,
                        'prescriptions': prescriptions,
                        'total_amount': total_amount,
                        'consultation': consultation,
                        'patient': patient,
                    }
                    return render(request, self.template_name, context)
                except Exception as e:
                    logger.error(f"Error saving data: {str(e)}")
                    messages.error(request, f'Error saving data: {str(e)}')
                    # Re-render form with context instead of redirecting
                    context = {
                        'form': form,
                        'consultation_code': consultation_code,
                        'prescriptions': prescriptions,
                        'total_amount': total_amount,
                        'consultation': consultation,
                        'patient': patient,
                    }
                    return render(request, self.template_name, context)
            else:
                logger.error(f"Form errors: {form.errors}")
                messages.error(request, f'Form validation failed: {form.errors}')
                
        except Consultation.DoesNotExist:
            messages.error(request, 'Consultation with this code does not exist')
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            messages.error(request, f'An unexpected error occurred: {str(e)}')
        
        # If we get here, something went wrong
        context = {
            'form': form,
            'consultation_code': consultation_code,
            'prescriptions': prescriptions if 'prescriptions' in locals() else [],
            'total_amount': sum(
                prescription.quantity * prescription.medicine.unit_price 
                for prescription in prescriptions
            ) if prescriptions else 0,
            'consultation': consultation if 'consultation' in locals() else None,
            'patient': patient,
        }
        return render(request, self.template_name, context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, View
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from .models import OverTheCounterSale, OverTheCounterSaleItem, Medicine
from .forms import OverTheCounterSaleForm, OverTheCounterSaleItemFormSet

import logging
logger = logging.getLogger(__name__)


class OverTheCounterSaleListView(LoginRequiredMixin, ListView):
    """View to list all over-the-counter sales."""
    model = OverTheCounterSale
    template_name = 'pharmacy/otc_sale_list.html'
    context_object_name = 'sales'
    paginate_by = 10
    ordering = ['-created_at']


class OverTheCounterSaleDetailView(LoginRequiredMixin, DetailView):
    """View to display details of a specific over-the-counter sale."""
    model = OverTheCounterSale
    template_name = 'pharmacy/otc_sale_detail.html'
    context_object_name = 'sale'


class CreateOverTheCounterSaleView(LoginRequiredMixin, View):
    """View to create a new over-the-counter sale."""
    template_name = 'pharmacy/create_otc_sale.html'
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests: display the sale form and an empty formset."""
        form = OverTheCounterSaleForm()
        formset = OverTheCounterSaleItemFormSet(prefix='items')
        medicines = Medicine.objects.filter(quantity_in_stock__gt=0).values('id', 'name', 'unit_price', 'quantity_in_stock')
        
        context = {
            'form': form,
            'formset': formset,
            'medicines': list(medicines),  # Convert to list for JSON serialization in template
        }
        return render(request, self.template_name, context)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Handle POST requests: process the form and formset data."""
        form = OverTheCounterSaleForm(request.POST)
        formset = OverTheCounterSaleItemFormSet(request.POST, prefix='items')
        
        if form.is_valid() and formset.is_valid():
            try:
                # Save the sale but don't commit yet
                sale = form.save(commit=False)
                sale.cashier = request.user
                
                # Calculate total amount from formset
                total_amount = 0
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        medicine = form.cleaned_data.get('medicine')
                        quantity = form.cleaned_data.get('quantity', 0)
                        unit_price = form.cleaned_data.get('unit_price', 0)
                        total_amount += quantity * unit_price
                
                sale.total_amount = total_amount
                sale.save()
                logger.info(f"Created OTC sale with ID: {sale.sale_id}")
                
                # Now save the formset (sale items)
                instances = formset.save(commit=False)
                
                # Check for sufficient stock and update medicine quantities
                for instance in instances:
                    if instance.medicine.quantity_in_stock < instance.quantity:
                        raise ValueError(f"Insufficient stock for {instance.medicine.name}")
                    
                    instance.sale = sale
                    instance.save()
                    logger.info(f"Added item: {instance.quantity} x {instance.medicine.name}")
                    
                    # Update medicine stock
                    medicine = instance.medicine
                    medicine.quantity_in_stock -= instance.quantity
                    medicine.save()
                    logger.info(f"Updated stock for {medicine.name}: {medicine.quantity_in_stock}")
                
                # Process any formset deletions (shouldn't be needed for a new sale, but included for completeness)
                for obj in formset.deleted_objects:
                    obj.delete()
                
                messages.success(request, f'Over-the-counter sale {sale.sale_id} created successfully!')
                return redirect('otc_sale_detail', pk=sale.pk)
                
            except ValueError as e:
                messages.error(request, str(e))
                transaction.set_rollback(True)
            except Exception as e:
                logger.error(f"Error creating OTC sale: {str(e)}")
                messages.error(request, f"An error occurred: {str(e)}")
                transaction.set_rollback(True)
        else:
            if not form.is_valid():
                logger.error(f"Form errors: {form.errors}")
                messages.error(request, f"Form validation failed: {form.errors}")
            if not formset.is_valid():  
                logger.error(f"Formset errors: {formset.errors}, {formset.non_form_errors()}")
                messages.error(request, f"Item validation failed. Please check quantities and selections.")
        
        # If we get here, something went wrong - reload the form with current data
        medicines = Medicine.objects.filter(quantity_in_stock__gt=0).values('id', 'name', 'unit_price', 'quantity_in_stock')
        context = {
            'form': form,
            'formset': formset,
            'medicines': list(medicines),
        }
        return render(request, self.template_name, context)


class GetMedicineInfoView(LoginRequiredMixin, View):
    """API view to get medicine details for AJAX requests."""
    
    def get(self, request, *args, **kwargs):
        medicine_id = request.GET.get('medicine_id')
        
        try:
            medicine = Medicine.objects.get(id=medicine_id)
            data = {
                'unit_price': float(medicine.unit_price),
                'quantity_in_stock': medicine.quantity_in_stock,
                'success': True
            }
            return JsonResponse(data)
        except Medicine.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Medicine not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Error fetching medicine info: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Conversation, Message, ReceptionQueue, Patient, User
import json

@login_required
def chat_home(request):
    # Get all users that the current user can chat with (doctors, admins, or receptionists)
    if request.user.user_type in ['DOCTOR', 'ADMIN']:
        chat_partners = User.objects.filter(user_type='RECEPTIONIST').exclude(id=request.user.id)
    else:
        chat_partners = User.objects.filter(
            Q(user_type='DOCTOR') | Q(user_type='ADMIN')
        ).exclude(id=request.user.id)
    
    # Get active patient if any
    active_patient_id = request.GET.get('patient_id')
    active_patient = None
    if active_patient_id:
        active_patient = get_object_or_404(Patient, id=active_patient_id)
    
    return render(request, 'communication/chat_home.html', {
        'chat_partners': chat_partners,
        'active_patient': active_patient
    })

@login_required
def conversation(request, user_id, patient_id=None):
    other_user = get_object_or_404(User, id=user_id)
    patient = None
    
    if patient_id:
        patient = get_object_or_404(Patient, id=patient_id)
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        participant1=request.user,
        participant2=other_user,
        patient=patient
    )
    
    # Mark messages as read
    Message.objects.filter(
        conversation=conversation,
        sender=other_user,
        is_read=False
    ).update(is_read=True)
    
    messages = conversation.messages.all().order_by('timestamp')
    
    return render(request, 'communication/conversation.html', {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user,
        'patient': patient
    })

@login_required
@require_POST
def send_message(request):
    data = json.loads(request.body)
    conversation_id = data.get('conversation_id')
    content = data.get('content')
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in [conversation.participant1, conversation.participant2]:
        return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)
    
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    
    return JsonResponse({
        'status': 'success',
        'message': {
            'content': message.content,
            'timestamp': message.timestamp.strftime('%b %d, %Y %I:%M %p'),
            'sender_id': message.sender.id
        }
    })

@login_required
def get_new_messages(request, conversation_id, last_message_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in [conversation.participant1, conversation.participant2]:
        return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)
    
    new_messages = conversation.messages.filter(
        id__gt=last_message_id,
        sender=conversation.participant2 if request.user == conversation.participant1 else conversation.participant1
    ).order_by('timestamp')
    
    # Mark as read
    new_messages.update(is_read=True)
    
    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%b %d, %Y %I:%M %p'),
        'sender_id': msg.sender.id
    } for msg in new_messages]
    
    return JsonResponse({
        'status': 'success',
        'messages': messages_data
    })

@login_required
def call_patient(request, patient_id):
    if request.user.user_type not in ['DOCTOR', 'ADMIN']:
        return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)
    
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get or create reception queue
    queue, created = ReceptionQueue.objects.get_or_create(receptionist=request.user)
    queue.current_patient = patient
    queue.is_available = False
    queue.save()
    
    # Send notification to reception (placeholder comment)
    
    return JsonResponse({'status': 'success', 'patient_name': patient.get_full_name()})

@login_required
def next_patient(request):
    if request.user.user_type != 'RECEPTIONIST':
        return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)
    
    queue = get_object_or_404(ReceptionQueue, receptionist=request.user)
    queue.current_patient = None
    queue.is_available = True
    queue.save()
    
    return JsonResponse({'status': 'success'})

