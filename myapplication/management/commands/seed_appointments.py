from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
import random

from myapplication.models import Appointment, Patient  # replace `your_app` with actual app name

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed appointments with 20–37 entries per patient per month'

    def handle(self, *args, **kwargs):
        doctors = User.objects.filter(user_type='DOCTOR')
        receptionists = User.objects.filter(user_type='RECEPTIONIST')
        patients = Patient.objects.all()
        
        if not doctors.exists() or not patients.exists():
            self.stdout.write(self.style.ERROR("❌ No doctors or patients found. Add them first."))
            return
        
        now = timezone.now()
        months = [0, 1, 2]  # Current month and past 2 months

        for patient in patients:
            for month_offset in months:
                base_date = now.replace(day=1) - timedelta(days=30 * month_offset)
                appointment_count = random.randint(20, 37)

                for _ in range(appointment_count):
                    doctor = random.choice(doctors)
                    receptionist = random.choice(receptionists) if receptionists.exists() else None

                    hour = random.randint(8, 16)
                    minute = random.choice([0, 15, 30, 45])
                    day = random.randint(1, 28)

                    start_datetime = datetime(base_date.year, base_date.month, day, hour, minute, tzinfo=timezone.get_current_timezone())
                    end_datetime = start_datetime + timedelta(minutes=random.choice([15, 30, 45, 60]))

                    Appointment.objects.create(
                        patient=patient,
                        doctor=doctor,
                        receptionist=receptionist,
                        scheduled_time=start_datetime,
                        end_time=end_datetime,
                        status=random.choice([c[0] for c in Appointment.STATUS_CHOICES]),
                        reason=f"Visit for general checkup ({random.randint(100, 999)})",
                        symptoms="Headache, fatigue" if random.random() > 0.3 else ""
                    )

                self.stdout.write(self.style.SUCCESS(
                    f"✔ Seeded {appointment_count} appointments for {patient} in {base_date.strftime('%B %Y')}"
                ))

        self.stdout.write(self.style.SUCCESS("✅ All appointments seeded successfully."))
