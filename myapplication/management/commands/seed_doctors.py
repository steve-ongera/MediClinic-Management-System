from django.core.management.base import BaseCommand
from datetime import date, timedelta
from random import choice, randint
from myapplication.models import Doctor

class Command(BaseCommand):
    help = 'Seed the database with 12 Kenyan doctors (without using Faker)'

    def handle(self, *args, **kwargs):
        if Doctor.objects.count() >= 12:
            self.stdout.write(self.style.WARNING('Doctors already seeded or exist. Skipping...'))
            return

        first_names = ['Brian', 'Wanjiku', 'David', 'Njeri', 'Peter', 'Achieng', 'James', 'Mwangi', 'Emily', 'Otieno', 'Mary', 'Kiplagat']
        last_names = ['Odhiambo', 'Kamau', 'Wambui', 'Ochieng', 'Kariuki', 'Mutua', 'Chebet', 'Wekesa', 'Kilonzo', 'Njoroge', 'Munyua', 'Okello']
        genders = ['M', 'F']
        blood_types = ['A+', 'B+', 'O+', 'AB+', 'O-', 'A-']
        specializations = ['GP', 'CAR', 'DER', 'PED', 'ORT', 'NEU', 'PSY', 'ONC', 'RAD', 'EM', 'ANES', 'OBGYN', 'ENT']
        departments = ['General Medicine', 'Cardiology', 'Dermatology', 'Pediatrics', 'Orthopedics']
        positions = ['Consultant', 'Resident', 'Senior Doctor', 'Medical Officer']

        doctors = []

        for i in range(12):
            first = first_names[i % len(first_names)]
            last = last_names[i % len(last_names)]
            gender = genders[i % len(genders)]
            specialization = specializations[i % len(specializations)]
            blood = blood_types[i % len(blood_types)]

            dob = date(1975 + i % 20, (i % 12) + 1, (i % 28) + 1)
            license_expiry = date.today() + timedelta(days=365 * (i % 3 + 1))

            doctor = Doctor(
                first_name=first,
                last_name=last,
                date_of_birth=dob,
                gender=gender,
                id_number=f'29{i:04d}56',
                national_id=f'20{i:04d}',
                passport_number=f'KP{i:04d}23',
                phone_number=f'+2547{i%10}{randint(10000000, 99999999)}',
                email=f'{first.lower()}.{last.lower()}@hospital.ke',
                emergency_contact='John Doe',
                emergency_phone='+254712345678',
                address='Moi Avenue',
                city='Nairobi',
                state='Nairobi County',
                country='Kenya',
                postal_code='00100',
                blood_type=blood,
                allergies='None',
                chronic_conditions='None',
                specialization=specialization,
                license_number=f'MCN{i:05d}',
                license_expiry=license_expiry,
                years_of_experience=randint(5, 30),
                qualifications='MBChB, MMed',
                bio='Experienced and compassionate doctor.',
                is_active=True,
                joining_date=date(2015 + (i % 5), 1, 10),
                department=choice(departments),
                position=choice(positions),
                working_days='Mon,Tue,Wed,Thu,Fri',
                working_hours='8:00 AM - 5:00 PM',
            )

            doctors.append(doctor)

        Doctor.objects.bulk_create(doctors)
        self.stdout.write(self.style.SUCCESS('Successfully seeded 12 Kenyan doctors!'))
