import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from myapplication.models import MedicineSale, Patient, SoldMedicine, Medicine

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate random medicine sales between Dec 12, 2024 and May 18, 2025'

    def handle(self, *args, **kwargs):
        # Define the date range specifically from Dec 12, 2024 to May 18, 2025
        start_date = datetime(2024, 12, 12)
        end_date = datetime(2025, 5, 18)

        payment_methods = ['CASH', 'MPESA', 'INSURANCE', 'CREDIT']
        patients = list(Patient.objects.all())
        receptionists = list(User.objects.filter(user_type='RECEPTIONIST'))
        medicines = list(Medicine.objects.all())

        if not patients or not receptionists or not medicines:
            self.stdout.write(self.style.ERROR("Ensure patients, receptionists, and medicines exist."))
            return

        # Calculate the total number of days in the range
        total_days = (end_date - start_date).days
        
        # Calculate how many sales to generate (averaging ~25 per month for the period)
        # The period is approximately 5 months, so we'll generate around 125 sales
        total_sales = random.randint(115, 135)
        
        self.stdout.write(f"Generating {total_sales} random sales between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}")

        # Generate the sales with random dates within the specified range
        for _ in range(total_sales):
            # Generate a random date within our range
            sale_date = self.random_date_in_range(start_date, end_date)
            
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
                notes=random.choice(['', 'Routine sale', 'Urgent need', 'Follow-up', 
                                    'Prescription refill', 'Emergency medication'])
            )

            total = Decimal('0.00')
            # Generate between 1 and 5 medicines per sale for more variety
            sold_medicines = random.sample(medicines, k=min(len(medicines), random.randint(1, 5)))
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

        self.stdout.write(self.style.SUCCESS(f"Successfully generated {total_sales} sales with random dates."))

    def random_date_in_range(self, start_date, end_date):
        delta = end_date - start_date
        random_day = random.randrange(delta.days + 1)
        random_time = timedelta(
            hours=random.randint(8, 18),  # More realistic business hours
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        return start_date + timedelta(days=random_day) + random_time