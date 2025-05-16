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




class AdminDashboardView(UserPassesTestMixin, View):
    template_name = 'admin/dashboard.html'
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'ADMIN'
    
    def get(self, request):
        # Date range filters
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
        
        # Get summary counts
        total_patients = Patient.objects.count()
        total_doctors = User.objects.filter(user_type='DOCTOR').count()
        total_medicines = Medicine.objects.count()
        total_revenue = MedicineSale.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Top 5 common diseases (from consultations)
        common_diseases = Disease.objects.annotate(
            count=Count('consultation')
        ).order_by('-count')[:5]
        
        disease_labels = [disease.name for disease in common_diseases]
        disease_counts = [disease.count for disease in common_diseases]
        
        # Best selling medicines
        best_selling = SoldMedicine.objects.values(
            'medicine__name'
        ).annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5]
        
        medicine_labels = [item['medicine__name'] for item in best_selling]
        medicine_counts = [item['total_sold'] for item in best_selling]
        
        # Monthly sales data for the line chart
        sales_data = MedicineSale.objects.filter(
            sale_date__gte=start_date
        ).annotate(
            date=Trunc('sale_date', 'day', output_field=DateTimeField())
        ).values('date').annotate(
            total=Sum('total_amount')
        ).order_by('date')
        
        sales_dates = [item['date'].strftime('%Y-%m-%d') for item in sales_data]
        sales_amounts = [float(item['total']) for item in sales_data]
        
        # Payment method distribution
        payment_methods = MedicineSale.objects.filter(
            sale_date__gte=start_date
        ).values('payment_method').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ).order_by('-total')
        
        payment_labels = [method['payment_method'] for method in payment_methods]
        payment_totals = [float(method['total']) for method in payment_methods]
        
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
        
        return render(request, self.template_name, context)


