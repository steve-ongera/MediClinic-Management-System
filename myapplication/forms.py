
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




from django import forms
from django.core.validators import RegexValidator
from .models import Doctor


class DoctorForm(forms.ModelForm):
    """
    Form for adding and editing doctors with custom validation and widgets.
    """
    
    # Custom validators
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    class Meta:
        model = Doctor
        fields = [
            # Personal Information
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'id_number', 'national_id', 'passport_number',
            # Contact Information
            'phone_number', 'alternate_phone', 'email',
            'emergency_contact', 'emergency_phone',
            # Address Information
            'address', 'city', 'state', 'country', 'postal_code',
            # Medical Information
            'blood_type', 'allergies', 'chronic_conditions',
            # Professional Information
            'specialization', 'license_number', 'license_expiry',
            'years_of_experience', 'qualifications', 'bio',
            # Hospital/Clinic Affiliation
            'is_active', 'joining_date', 'department', 'position',
            # System Information
            'profile_picture', 'signature',
            # Availability
            'working_days', 'working_hours',
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ID number'
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter national ID (optional)'
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter passport number (optional)'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'alternate_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890 (optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'doctor@email.com'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Full address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal/ZIP code'
            }),
            'blood_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List any known allergies'
            }),
            'chronic_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List any chronic conditions'
            }),
            'specialization': forms.Select(attrs={
                'class': 'form-control'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medical license number'
            }),
            'license_expiry': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'qualifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List qualifications, degrees, certifications'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Professional biography'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'joining_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Position/Title'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'signature': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'working_days': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mon,Tue,Wed,Thu,Fri'
            }),
            'working_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 9:00 AM - 5:00 PM'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add phone validators
        self.fields['phone_number'].validators.append(self.phone_validator)
        self.fields['alternate_phone'].validators.append(self.phone_validator)
        self.fields['emergency_phone'].validators.append(self.phone_validator)
        
        # Make certain fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['date_of_birth'].required = True
        self.fields['gender'].required = True
        self.fields['phone_number'].required = True
        self.fields['specialization'].required = True
        self.fields['license_number'].required = True
        
        # Add help text
        self.fields['working_days'].help_text = "Enter working days separated by commas (e.g., Mon,Tue,Wed,Thu,Fri)"
        self.fields['working_hours'].help_text = "Enter working hours (e.g., 9:00 AM - 5:00 PM)"
    
    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if id_number:
            # Check if another doctor has this ID number (excluding current instance)
            qs = Doctor.objects.filter(id_number=id_number)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A doctor with this ID number already exists.")
        return id_number
    
    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if license_number:
            # Check if another doctor has this license number (excluding current instance)
            qs = Doctor.objects.filter(license_number=license_number)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A doctor with this license number already exists.")
        return license_number
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if another doctor has this email (excluding current instance)
            qs = Doctor.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A doctor with this email already exists.")
        return email
    




from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User

class UserForm(UserCreationForm):
    """Form for creating a new user with Bootstrap styling"""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name',
            'autocomplete': 'given-name'
        }),
        help_text='Required. 150 characters or fewer.'
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name',
            'autocomplete': 'family-name'
        }),
        help_text='Required. 150 characters or fewer.'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address',
            'autocomplete': 'email'
        }),
        help_text='Required. Enter a valid email address.'
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username'
        }),
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password'
        }),
        help_text='Your password must contain at least 8 characters.'
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password'
        }),
        help_text='Enter the same password as before, for verification.'
    )
    
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_user_type'
        }),
        help_text='Select the user role.'
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number',
            'autocomplete': 'tel'
        }),
        help_text='Optional. Enter phone number with country code.'
    )
    
    specialization = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter medical specialization',
            'id': 'id_specialization'
        }),
        help_text='Required for doctors only.'
    )
    
    license_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter medical license number',
            'id': 'id_license_number'
        }),
        help_text='Required for doctors only.'
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_is_active'
        }),
        help_text='Designates whether this user should be treated as active.'
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'username', 
            'password1', 'password2', 'user_type', 'phone_number', 
            'specialization', 'license_number', 'is_active'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to inherited fields
        for field_name in self.fields:
            field = self.fields[field_name]
            if 'class' not in field.widget.attrs:
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs['class'] = 'form-check-input'
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs['class'] = 'form-select'
                else:
                    field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        specialization = cleaned_data.get('specialization')
        license_number = cleaned_data.get('license_number')

        # Validation for doctor fields
        if user_type == 'DOCTOR':
            if not specialization:
                self.add_error('specialization', 'Specialization is required for doctors.')
            if not license_number:
                self.add_error('license_number', 'License number is required for doctors.')
        
        return cleaned_data


class UserEditForm(forms.ModelForm):
    """Form for editing existing user with Bootstrap styling"""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name',
            'autocomplete': 'given-name'
        }),
        help_text='Required. 150 characters or fewer.'
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name',
            'autocomplete': 'family-name'
        }),
        help_text='Required. 150 characters or fewer.'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address',
            'autocomplete': 'email'
        }),
        help_text='Required. Enter a valid email address.'
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'username'
        }),
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_user_type'
        }),
        help_text='Select the user role.'
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number',
            'autocomplete': 'tel'
        }),
        help_text='Optional. Enter phone number with country code.'
    )
    
    specialization = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter medical specialization',
            'id': 'id_specialization'
        }),
        help_text='Required for doctors only.'
    )
    
    license_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter medical license number',
            'id': 'id_license_number'
        }),
        help_text='Required for doctors only.'
    )
    
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_is_active'
        }),
        help_text='Designates whether this user should be treated as active.'
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'username', 
            'user_type', 'phone_number', 'specialization', 
            'license_number', 'is_active'
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to all fields
        for field_name in self.fields:
            field = self.fields[field_name]
            if 'class' not in field.widget.attrs:
                if isinstance(field.widget, forms.CheckboxInput):
                    field.widget.attrs['class'] = 'form-check-input'
                elif isinstance(field.widget, forms.Select):
                    field.widget.attrs['class'] = 'form-select'
                else:
                    field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and self.user.email == email:
            return email
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.user and self.user.username == username:
            return username
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with this username already exists.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        specialization = cleaned_data.get('specialization')
        license_number = cleaned_data.get('license_number')

        # Validation for doctor fields
        if user_type == 'DOCTOR':
            if not specialization:
                self.add_error('specialization', 'Specialization is required for doctors.')
            if not license_number:
                self.add_error('license_number', 'License number is required for doctors.')
        
        return cleaned_data


class PasswordChangeForm(forms.Form):
    """Bootstrap-styled password change form"""
    
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password',
            'autocomplete': 'current-password'
        }),
        help_text='Enter your current password.'
    )
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        }),
        help_text='Your password must contain at least 8 characters.',
        validators=[validate_password]
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        }),
        help_text='Enter the same password as before, for verification.'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError('Your old password was entered incorrectly.')
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                self.add_error('new_password2', 'The two password fields didn\'t match.')

        return cleaned_data

    def save(self):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user