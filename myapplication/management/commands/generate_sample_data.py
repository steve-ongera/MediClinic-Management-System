import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from myapplication.models import Appointment, Consultation, Disease, Prescription, Medicine

class Command(BaseCommand):
    help = "Generate Consultations, Diseases, and Prescriptions for existing Appointments using index"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to add consultations, diseases, and prescriptions to existing appointments...")

        appointments = Appointment.objects.all().order_by('scheduled_time')
        diseases = list(Disease.objects.all())
        medicines = list(Medicine.objects.all())

        if not appointments:
            self.stdout.write(self.style.ERROR("No appointments found."))
            return

        if not diseases:
            self.stdout.write(self.style.ERROR("No diseases found."))
            return

        if not medicines:
            self.stdout.write(self.style.ERROR("No medicines found."))
            return

        for i, appointment in enumerate(appointments, start=1):
            # Skip if consultation already exists for this appointment (optional)
            if Consultation.objects.filter(appointment=appointment).exists():
                self.stdout.write(f"Consultation already exists for appointment {appointment.id}, skipping.")
                continue

            consultation = Consultation.objects.create(
                appointment=appointment,
                diagnosis=f"Diagnosis for appointment #{i}: signs of viral infection.",
                notes=f"Notes for appointment #{i}: advised rest and hydration.",
                follow_up_date=appointment.scheduled_time.date() + timedelta(days=14),
                follow_up_notes=f"Follow-up notes for appointment #{i}",
            )
            self.stdout.write(f"Created Consultation {consultation.id} for Appointment {appointment.id}")

            # Assign 2-3 random diseases
            selected_diseases = random.sample(diseases, k=min(3, len(diseases)))
            consultation.diseases.set(selected_diseases)

            # Create 1-2 prescriptions randomly
            selected_meds = random.sample(medicines, k=min(2, len(medicines)))
            for med in selected_meds:
                Prescription.objects.create(
                    consultation=consultation,
                    medicine=med,
                    dosage="500mg",
                    duration="7 days",
                    instructions="Take after meals",
                    quantity=14
                )
            self.stdout.write(f"Created {len(selected_meds)} Prescriptions for Consultation {consultation.id}")

        self.stdout.write(self.style.SUCCESS("All existing appointments processed successfully."))
