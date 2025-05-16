# MediClinic Management System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)

## Overview

MediClinic Management System is a comprehensive Django-based solution designed to streamline and automate the day-to-day operations of medical clinics and healthcare facilities. This system integrates patient management, appointment scheduling, consultation tracking, prescription management, and inventory control in one unified platform.

## Key Features

- **User Management**: Multi-level user access with specialized roles for administrators, doctors, and receptionists
- **Patient Records**: Complete digital patient profiles with medical history tracking
- **Appointment System**: Efficient scheduling and management of patient appointments
- **Consultation & Diagnosis**: Detailed consultation records with disease tracking and follow-up management
- **Pharmacy Integration**: Medication inventory control and prescription management
- **Billing System**: Integrated payment processing with multiple payment methods support
- **Notifications**: Automated alerts for appointments, inventory, and follow-ups
- **Clinic Configuration**: Customizable settings to match your facility's specific needs

## System Architecture

The system is built on Django framework with a well-structured database design including:

- User authentication and authorization
- Patient information management
- Medical record keeping
- Appointment scheduling
- Prescription and medication management
- Financial transactions tracking
- System settings and configuration

## Installation

### Prerequisites

- Python 3.8+
- Django 4.0+
- PostgreSQL (recommended) or MySQL
- pip (Python package manager)

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mediclinic-management.git
   cd mediclinic-management
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your database in `settings.py`

5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the admin interface at `http://localhost:8000/admin`

## User Roles and Permissions

### Administrator
- Full system access
- User management
- System configuration
- Reports generation

### Doctor
- View and manage patient records
- Create consultations and prescriptions
- View appointment schedule
- Receive notifications

### Receptionist
- Register new patients
- Schedule appointments
- Process medicine sales
- Handle basic billing

## Data Models

The system utilizes the following key data models:

- **User**: System users with role-based permissions
- **Patient**: Complete patient information
- **Appointment**: Patient-doctor scheduling
- **Consultation**: Medical diagnoses and treatment plans
- **Disease**: Medical condition catalog
- **Medicine & MedicineCategory**: Pharmaceutical inventory
- **Prescription**: Medication instructions
- **MedicineSale & SoldMedicine**: Pharmacy transactions
- **PatientMedicalHistory**: Long-term patient health records
- **Notification**: System alerts and reminders
- **ClinicSettings**: Facility configuration

## Customization

The system is designed to be highly adaptable to different clinic workflows and requirements:

- Adjust appointment duration settings
- Configure working hours
- Customize patient capacity
- Modify notification preferences
- Set up clinic branding elements

## Security Features

- Role-based access control
- Password protection
- Secure patient data handling
- Activity logging

## Support and Contribution

For issues, feature requests, or contributions, please open an issue or submit a pull request on our GitHub repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Django Project
- Bootstrap
- Chart.js
- DataTables
