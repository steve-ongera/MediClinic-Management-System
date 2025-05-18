from django.core.management.base import BaseCommand
from myapplication.models import Patient, Consultation, PatientMedicalHistory

from django.utils.timezone import now
import random
from datetime import timedelta
from django.contrib.auth import get_user_model


User = get_user_model()

class Command(BaseCommand):
    help = 'Generate sample PatientMedicalHistory records'

    def handle(self, *args, **kwargs):
        patients = list(Patient.objects.all())
        consultations = list(Consultation.objects.all())
        users = list(User.objects.all())

        if len(patients) < 5 or len(users) < 1:
            self.stdout.write(self.style.ERROR("Ensure you have at least 5 patients and 1 user."))
            return

        record_types = ['Allergy', 'Surgery', 'Chronic Condition', 'Medication', 'Injury']
        descriptions = [
            "Patient reported mild allergic reaction to penicillin.",
            "Underwent appendectomy in 2018 with no complications.",
            "Diagnosed with type 2 diabetes, on metformin.",
            "Prescribed blood pressure medication.",
            "Fractured left wrist, currently in recovery.",
            "Suffers from seasonal pollen allergies.",
            "Completed knee surgery successfully last month.",
            "Has asthma diagnosed during childhood.",
            "Regular migraine complaints, requires follow-ups.",
            "Recently diagnosed with high cholesterol."
        ]

        count = 20
        created = 0

        for i in range(count):
            patient = patients[i % len(patients)]
            consultation = consultations[i % len(consultations)] if consultations else None
            record_type = random.choice(record_types)
            description = random.choice(descriptions)
            recorded_by = users[i % len(users)]
            date_recorded = now().date() - timedelta(days=random.randint(1, 365))

            record = PatientMedicalHistory.objects.create(
                patient=patient,
                consultation=consultation,
                record_type=record_type,
                description=description,
                date_recorded=date_recorded,
                recorded_by=recorded_by
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created} PatientMedicalHistory records.'))
