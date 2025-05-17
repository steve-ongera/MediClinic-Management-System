import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from myapplication.models import MedicineSale, Patient  # Replace 'myapp' with your actual app name

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate between 20 to 26 random medicine sales per month from May 1st, 2024 to May 17th, 2025'

    def handle(self, *args, **kwargs):
        start_date = datetime(2024, 5, 1)
        end_date = datetime(2025, 5, 17)

        payment_methods = ['CASH', 'MPESA', 'INSURANCE', 'CREDIT']
        
        patients = list(Patient.objects.all())
        receptionists = list(User.objects.filter(user_type='RECEPTIONIST'))

        if not patients or not receptionists:
            self.stdout.write(self.style.ERROR("Make sure at least one patient and one receptionist exist."))
            return

        current = start_date.replace(day=1)
        while current <= end_date:
            year = current.year
            month = current.month

            # Get max day of the month
            next_month = current.replace(day=28) + timedelta(days=4)
            last_day = (next_month - timedelta(days=next_month.day)).day
            month_end = datetime(year, month, last_day)
            if month_end > end_date:
                month_end = end_date

            self.stdout.write(f"Creating sales for {year}-{month:02d}")

            for _ in range(random.randint(20, 26)):
                sale_date = self.random_date_in_range(current, month_end)
                payment_method = random.choice(payment_methods)
                mpesa_number = '07' + ''.join(random.choices('0123456789', k=8)) if payment_method == 'MPESA' else None
                mpesa_code = 'MP' + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8)) if payment_method == 'MPESA' else None

                MedicineSale.objects.create(
                    patient=random.choice(patients),
                    receptionist=random.choice(receptionists),
                    payment_method=payment_method,
                    mpesa_number=mpesa_number,
                    mpesa_code=mpesa_code,
                    total_amount=round(random.uniform(100.00, 5000.00), 2),
                    sale_date=timezone.make_aware(sale_date),
                    notes=random.choice(['', 'Routine sale', 'Urgent need', 'Follow-up'])
                )

            # Move to next month
            if month == 12:
                current = current.replace(year=year + 1, month=1)
            else:
                current = current.replace(month=month + 1)

        self.stdout.write(self.style.SUCCESS("Sales generation complete."))

    def random_date_in_range(self, start_date, end_date):
        delta = end_date - start_date
        random_day = random.randrange(delta.days + 1)
        random_time = timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        return start_date + timedelta(days=random_day) + random_time