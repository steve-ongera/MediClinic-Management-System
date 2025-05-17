
from django import forms
from .models import Patient

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )



class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'id_number', 'phone_number', 'email', 'address',
            'blood_type', 'allergies'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'



from django import forms
from .models import Patient, Appointment, Consultation, Prescription, Disease, Medicine
from django.contrib.auth import get_user_model
User = get_user_model()

class PatientSearchForm(forms.Form):
    search_query = forms.CharField(
        label='Search Patient',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter patient name or ID number',
            'id': 'patient-search'
        })
    )

from django import forms
from .models import Patient, Appointment, Consultation, Prescription, Disease, Medicine
from django.contrib.auth import get_user_model

User = get_user_model()

class PatientSearchForm(forms.Form):
    search_query = forms.CharField(
        label='Search Patient',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter patient name or ID number',
            'id': 'patient-search',
            'autocomplete': 'off'
        })
    )

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'scheduled_time', 'reason', 'symptoms']
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-control select2',
                'id': 'patient-select',
                'style': 'width: 100%'
            }),
            'doctor': forms.Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%'
            }),
            'scheduled_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter reason for visit...'
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe symptoms...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(user_type='DOCTOR')
        self.fields['patient'].required = False
        self.fields['doctor'].widget.attrs.update({'data-placeholder': 'Select doctor...'})
        self.fields['scheduled_time'].widget.attrs.update({'placeholder': 'Select date and time...'})

class ConsultationForm(forms.ModelForm):
    diseases = forms.ModelMultipleChoiceField(
        queryset=Disease.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2-multiple',
            'style': 'width: 100%',
            'data-placeholder': 'Select diseases/conditions...'
        }),
        required=False
    )
    
    class Meta:
        model = Consultation
        fields = ['diagnosis', 'diseases', 'notes', 'follow_up_date', 'follow_up_notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter diagnosis...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter clinical notes...'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Select follow-up date...'
            }),
            'follow_up_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter follow-up instructions...'
            }),
        }

class PrescriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medicine'].widget.attrs.update({
            'class': 'form-control select2',
            'style': 'width: 100%',
            'data-placeholder': 'Select medicine...'
        })
    
    class Meta:
        model = Prescription
        fields = ['medicine', 'dosage', 'duration', 'instructions', 'quantity']
        widgets = {
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 500mg twice daily'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 7 days'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Take with meals'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Quantity'
            }),
        }

class PrescriptionFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = True
            # Add Bootstrap classes to all fields in the formset
            for field in form.fields.values():
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'