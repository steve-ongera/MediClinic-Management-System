from django.core.management.base import BaseCommand
from myapplication.models import MedicineCategory

class Command(BaseCommand):
    help = 'Generate 25 medicine categories for the MedicineCategory model'

    def handle(self, *args, **options):
        # List of realistic medicine categories with descriptions
        medicine_categories = [
            {
                "name": "Analgesics",
                "description": "Medications used to relieve pain without causing loss of consciousness."
            },
            {
                "name": "Antibiotics",
                "description": "Medications that kill or inhibit the growth of bacteria."
            },
            {
                "name": "Antidepressants",
                "description": "Medications used to treat major depressive disorder and other conditions."
            },
            {
                "name": "Antifungals",
                "description": "Medications used to treat fungal infections."
            },
            {
                "name": "Antihistamines",
                "description": "Medications that oppose the activity of histamine receptors in the body."
            },
            {
                "name": "Antihypertensives",
                "description": "Medications used to treat high blood pressure (hypertension)."
            },
            {
                "name": "Anti-inflammatories",
                "description": "Medications used to reduce inflammation and treat related pain."
            },
            {
                "name": "Antimalarials",
                "description": "Medications used for the treatment and prevention of malaria."
            },
            {
                "name": "Antivirals",
                "description": "Medications used to treat viral infections."
            },
            {
                "name": "Bronchodilators",
                "description": "Medications that dilate the bronchi and bronchioles, decreasing resistance in the respiratory airway."
            },
            {
                "name": "Cardiovascular Drugs",
                "description": "Medications used to treat diseases that affect the heart or blood vessels."
            },
            {
                "name": "Dermatologicals",
                "description": "Medications used to treat conditions affecting the skin."
            },
            {
                "name": "Diuretics",
                "description": "Medications that increase the amount of water and salt expelled from the body as urine."
            },
            {
                "name": "Gastrointestinal Drugs",
                "description": "Medications that affect the gastrointestinal tract or digestive system."
            },
            {
                "name": "Hormones",
                "description": "Synthetic versions of hormones produced by the body or medications that affect hormone levels."
            },
            {
                "name": "Immunosuppressants",
                "description": "Medications that suppress or reduce the strength of the body's immune system."
            },
            {
                "name": "Lipid-lowering Agents",
                "description": "Medications used to lower lipid levels in the blood."
            },
            {
                "name": "Muscle Relaxants",
                "description": "Medications that affect skeletal muscle function and decrease muscle tone."
            },
            {
                "name": "Neurological Drugs",
                "description": "Medications used to treat disorders of the nervous system."
            },
            {
                "name": "Ophthalmics",
                "description": "Medications used to treat disorders of the eye."
            },
            {
                "name": "Psychotropics",
                "description": "Medications that affect brain function, altering perceptions, mood, consciousness, or behavior."
            },
            {
                "name": "Respiratory Drugs",
                "description": "Medications used to treat respiratory disorders, such as asthma or COPD."
            },
            {
                "name": "Sedatives",
                "description": "Medications that induce sedation by reducing irritability or excitement."
            },
            {
                "name": "Vaccines",
                "description": "Biological preparations that provide active acquired immunity to a particular infectious disease."
            },
            {
                "name": "Vitamins & Supplements",
                "description": "Substances used to supplement the diet to improve health and wellness."
            }
        ]

        count = 0
        for category in medicine_categories:
            # Check if category already exists
            if not MedicineCategory.objects.filter(name=category["name"]).exists():
                MedicineCategory.objects.create(
                    name=category["name"],
                    description=category["description"]
                )
                count += 1
                self.stdout.write(self.style.SUCCESS(f"Created category: {category['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Category already exists: {category['name']}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} new medicine categories"))
        self.stdout.write(f"Total medicine categories: {MedicineCategory.objects.count()}")