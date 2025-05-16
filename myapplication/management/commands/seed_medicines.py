from django.core.management.base import BaseCommand
from myapplication.models import Medicine, MedicineCategory
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = "Seeds the database with 50 common medicines for diseases in Kenya"

    def handle(self, *args, **kwargs):
        diseases_and_medicines = [
            ("Malaria", "Artemether-Lumefantrine"),
            ("Typhoid", "Ciprofloxacin"),
            ("Tuberculosis", "Rifampicin"),
            ("HIV/AIDS", "Dolutegravir"),
            ("Diabetes", "Metformin"),
            ("Hypertension", "Amlodipine"),
            ("Asthma", "Salbutamol"),
            ("Pneumonia", "Azithromycin"),
            ("Diarrhea", "ORS and Zinc"),
            ("Urinary Tract Infection", "Nitrofurantoin"),
            ("Ringworm", "Clotrimazole"),
            ("Peptic Ulcer", "Omeprazole"),
            ("COVID-19", "Paracetamol"),
            ("Flu", "Antihistamines"),
            ("Measles", "Vitamin A"),
            ("Meningitis", "Ceftriaxone"),
            ("Skin infections", "Fusidic Acid"),
            ("Conjunctivitis", "Chloramphenicol"),
            ("Worm Infestation", "Albendazole"),
            ("Migraine", "Ibuprofen"),
            ("Otitis Media", "Amoxicillin"),
            ("Anemia", "Iron Supplements"),
            ("Dental Caries", "Metronidazole"),
            ("Chickenpox", "Calamine Lotion"),
            ("Scabies", "Permethrin"),
            ("Brucellosis", "Doxycycline"),
            ("Gonorrhea", "Cefixime"),
            ("Syphilis", "Benzathine Penicillin"),
            ("Hepatitis B", "Entecavir"),
            ("Rickets", "Vitamin D"),
            ("Malnutrition", "PlumpyNut"),
            ("Snake Bite", "Antivenom"),
            ("Burns", "Silver Sulfadiazine"),
            ("Eye Infections", "Tetracycline Eye Ointment"),
            ("Allergies", "Loratadine"),
            ("Back Pain", "Diclofenac"),
            ("Headache", "Paracetamol"),
            ("Jiggers", "Hydrogen Peroxide"),
            ("Bilharzia", "Praziquantel"),
            ("Dysentery", "Metronidazole"),
            ("Tonsillitis", "Erythromycin"),
            ("Eczema", "Hydrocortisone Cream"),
            ("Cholera", "Doxycycline"),
            ("Whooping Cough", "Erythromycin"),
            ("Yellow Fever", "Supportive Therapy"),
            ("Leprosy", "Dapsone"),
            ("Polio", "Polio Vaccine"),
            ("Tetanus", "Tetanus Toxoid"),
            ("Rabies", "Rabies Vaccine"),
            ("Hemorrhoids", "Lidocaine Ointment")
        ]

        category, _ = MedicineCategory.objects.get_or_create(name="General")

        for index, (disease, med_name) in enumerate(diseases_and_medicines):
            medicine, created = Medicine.objects.get_or_create(
                name=med_name,
                defaults={
                    "category": category,
                    "description": f"Used for treating {disease}",
                    "quantity_in_stock": random.randint(10, 100),
                    "unit_price": round(random.uniform(50.0, 1000.0), 2),
                    "reorder_level": 10,
                    "manufacturer": f"Generic Pharma {index + 1}",
                    "expiry_date": date.today() + timedelta(days=random.randint(365, 1095)),
                    "batch_number": f"BN{random.randint(10000, 99999)}"
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✔ Created: {med_name} for {disease}"))
            else:
                self.stdout.write(self.style.WARNING(f"✖ Already exists: {med_name}"))

        self.stdout.write(self.style.SUCCESS("✅ Seeding completed."))
