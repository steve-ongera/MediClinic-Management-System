import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from myapplication.models import MedicineSale, Patient, SoldMedicine, Medicine  # Replace 'myapp' with your app name

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate 20-26 medicine sales per month from May 1, 2024 to May 17, 2025, including SoldMedicine'

    def handle(self, *args, **kwargs):
        start_date = datetime(2024, 5, 1)
        end_date = datetime(2025, 5, 17)

        payment_methods = ['CASH', 'MPESA', 'INSURANCE', 'CREDIT']
        patients = list(Patient.objects.all())
        receptionists = list(User.objects.filter(user_type='RECEPTIONIST'))
        medicines = list(Medicine.objects.all())

        if not patients or not receptionists or not medicines:
            self.stdout.write(self.style.ERROR("Ensure patients, receptionists, and medicines exist."))
            return

        current = start_date.replace(day=1)
        while current <= end_date:
            year = current.year
            month = current.month
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

                sale = MedicineSale.objects.create(
                    patient=random.choice(patients),
                    receptionist=random.choice(receptionists),
                    payment_method=payment_method,
                    mpesa_number=mpesa_number,
                    mpesa_code=mpesa_code,
                    total_amount=0,  # will be updated later
                    sale_date=timezone.make_aware(sale_date),
                    notes=random.choice(['', 'Routine sale', 'Urgent need', 'Follow-up'])
                )

                total = Decimal('0.00')
                sold_medicines = random.sample(medicines, k=min(len(medicines), random.randint(3, 4)))
                for medicine in sold_medicines:
                    unit_price = round(random.uniform(50.0, 1000.0), 2)
                    quantity = random.randint(1, 5)
                    SoldMedicine.objects.create(
                        sale=sale,
                        medicine=medicine,
                        quantity=quantity,
                        unit_price=unit_price
                    )
                    total += Decimal(str(unit_price)) * quantity

                sale.total_amount = round(total, 2)
                sale.save()

            if month == 12:
                current = current.replace(year=year + 1, month=1)
            else:
                current = current.replace(month=month + 1)

        self.stdout.write(self.style.SUCCESS("Sales and SoldMedicine generation complete."))

    def random_date_in_range(self, start_date, end_date):
        delta = end_date - start_date
        random_day = random.randrange(delta.days + 1)
        random_time = timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        return start_date + timedelta(days=random_day) + random_time
