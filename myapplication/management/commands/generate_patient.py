from django.core.management.base import BaseCommand
from myapplication.models import Patient
from django.utils import timezone
import random
import datetime

class Command(BaseCommand):
    help = 'Generate 20 sample Kenyan patients'

    def handle(self, *args, **options):
        # Kenyan first names
        kenyan_first_names = [
            # Male names
            'Wafula', 'Kamau', 'Omondi', 'Mwangi', 'Kipchoge', 'Ruto', 'Kiptoo', 'Maina', 
            'Otieno', 'Kariuki', 'Njoroge', 'Kimani', 'Odhiambo', 'Kiprono', 'Korir',
            # Female names
            'Wangari', 'Akinyi', 'Wanjiku', 'Auma', 'Nyambura', 'Atieno', 'Njeri', 
            'Muthoni', 'Owino', 'Chebet', 'Kemunto', 'Moraa', 'Wambui', 'Adhiambo', 'Chepkoech'
        ]
        
        # Kenyan last names
        kenyan_last_names = [
            'Kamau', 'Ochieng', 'Wekesa', 'Muthoni', 'Kiptanui', 'Onyango', 'Kimutai', 
            'Ndung\'u', 'Mutiso', 'Mbugua', 'Njenga', 'Omondi', 'Kipkemoi', 'Njuguna', 
            'Mugo', 'Wanjiru', 'Gitau', 'Karanja', 'Wafula', 'Ogutu'
        ]
        
        # Kenyan counties/towns for addresses
        kenyan_locations = [
            'Nairobi', 'Kiambu', 'Nakuru', 'Mombasa', 'Kisumu', 'Eldoret', 'Thika', 
            'Nyeri', 'Machakos', 'Kitale', 'Kericho', 'Kakamega', 'Kisii', 'Garissa', 
            'Meru', 'Embu', 'Malindi', 'Bungoma', 'Naivasha', 'Kitui'
        ]
        
        # Common blood types
        blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        
        # Common allergies (some can be None)
        allergies_list = [
            'Peanuts', 'Dust', 'Pollen', 'Penicillin', 'Shellfish', 'Dairy', 
            'Wheat', 'Eggs', 'Nuts', 'Latex', None, None, None, None, None
        ]
        
        # Email domains
        email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        
        patients_created = 0
        attempts = 0
        max_attempts = 100  # Prevent infinite loops
        
        self.stdout.write('Generating 20 Kenyan patients...')
        
        while patients_created < 20 and attempts < max_attempts:
            attempts += 1
            
            # Determine gender
            gender = random.choice(['M', 'F'])
            
            # Choose name based on gender
            if gender == 'M':
                first_name = random.choice([name for name in kenyan_first_names 
                                           if kenyan_first_names.index(name) < 15])  # First 15 are male names
            else:
                first_name = random.choice([name for name in kenyan_first_names 
                                           if kenyan_first_names.index(name) >= 15])  # Last 15 are female names
                
            last_name = random.choice(kenyan_last_names)
            
            # Generate date of birth (between 18 and 80 years ago)
            today = timezone.now().date()
            age = random.randint(18, 80)
            year = today.year - age
            month = random.randint(1, 12)
            day = random.randint(1, 28)  # Safe for all months
            date_of_birth = datetime.date(year, month, day)
            
            # Generate Kenyan ID number (7-8 digits)
            id_number = str(random.randint(10000000, 39999999))
            
            # Generate Kenyan phone number (format: 07XX XXX XXX or 01XX XXX XXX)
            prefix = random.choice(['07', '01'])
            phone_number = f"+254{prefix}{random.randint(10000000, 99999999)}"
            
            # Generate email (can be None for some patients)
            if random.random() > 0.3:  # 70% chance of having an email
                username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
                email = f"{username}@{random.choice(email_domains)}"
            else:
                email = None
                
            # Generate address
            address = f"P.O. Box {random.randint(1, 9999)}, {random.choice(kenyan_locations)}, Kenya"
            
            # Generate blood type (can be None for some patients)
            blood_type = random.choice(blood_types) if random.random() > 0.4 else None
            
            # Generate allergies (can be None for some patients)
            allergies = random.choice(allergies_list)
            
            # Create the patient
            try:
                patient = Patient(
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    id_number=id_number,
                    phone_number=phone_number,
                    email=email,
                    address=address,
                    blood_type=blood_type,
                    allergies=allergies
                )
                patient.save()
                patients_created += 1
                self.stdout.write(f"Created patient: {patient}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to create patient: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {patients_created} Kenyan patients'))