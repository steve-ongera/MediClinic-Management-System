from django.core.management.base import BaseCommand
from myapplication.models import Disease

class Command(BaseCommand):
    help = 'Generate a list of diseases common in Kenya with ICD-10 codes'

    def handle(self, *args, **options):
        # List of diseases with their descriptions and ICD-10 codes
        diseases_data = [
            # Infectious and Parasitic Diseases
            {
                "name": "Malaria",
                "description": "A mosquito-borne disease caused by Plasmodium parasites, particularly prevalent in tropical regions of Kenya. Symptoms include fever, chills, and flu-like illness.",
                "icd_code": "B54"
            },
            {
                "name": "Tuberculosis (TB)",
                "description": "A bacterial infection primarily affecting the lungs, common in Kenya. It's caused by Mycobacterium tuberculosis and often presents with persistent cough, chest pain, and weight loss.",
                "icd_code": "A15-A19"
            },
            {
                "name": "HIV/AIDS",
                "description": "Human Immunodeficiency Virus infection that compromises the immune system. Kenya has made progress in reducing prevalence, but it remains a significant public health concern.",
                "icd_code": "B20-B24"
            },
            {
                "name": "Typhoid Fever",
                "description": "A bacterial infection caused by Salmonella typhi, spread through contaminated food and water. Common in areas with poor sanitation in Kenya.",
                "icd_code": "A01.0"
            },
            {
                "name": "Cholera",
                "description": "An acute diarrheal infection caused by Vibrio cholerae bacteria. Occurs in regions with inadequate water treatment and sanitation infrastructure.",
                "icd_code": "A00"
            },
            {
                "name": "Schistosomiasis (Bilharzia)",
                "description": "A parasitic disease caused by flatworms, common in communities living near freshwater lakes and rivers in Kenya.",
                "icd_code": "B65"
            },
            {
                "name": "Amoebiasis",
                "description": "An intestinal infection caused by the parasite Entamoeba histolytica, leading to dysentery and liver abscesses. Common in areas with poor sanitation.",
                "icd_code": "A06"
            },
            {
                "name": "Giardiasis",
                "description": "An intestinal infection caused by the parasite Giardia lamblia, often acquired from contaminated water sources.",
                "icd_code": "A07.1"
            },
            {
                "name": "Measles",
                "description": "A highly contagious viral disease still prevalent in some parts of Kenya, especially in under-vaccinated communities.",
                "icd_code": "B05"
            },
            {
                "name": "Pneumonia",
                "description": "An infection that inflames air sacs in the lungs. A leading cause of mortality in children under five in Kenya.",
                "icd_code": "J12-J18"
            },
            {
                "name": "Meningitis",
                "description": "Inflammation of the membranes surrounding the brain and spinal cord. Bacterial meningitis outbreaks occur periodically in parts of Kenya.",
                "icd_code": "G00-G03"
            },
            {
                "name": "Leishmaniasis",
                "description": "A parasitic disease spread by sandflies, causing skin sores or affecting internal organs. Prevalent in arid and semi-arid regions of Kenya.",
                "icd_code": "B55"
            },
            {
                "name": "Brucellosis",
                "description": "A bacterial infection transmitted from animals to humans through contaminated dairy products or direct contact. Common in pastoralist communities.",
                "icd_code": "A23"
            },
            {
                "name": "Trachoma",
                "description": "A bacterial eye infection causing corneal scarring and blindness if untreated. Endemic in some rural parts of Kenya.",
                "icd_code": "A71"
            },
            {
                "name": "Dengue Fever",
                "description": "A mosquito-borne viral disease causing fever, headaches, and joint pain. Increasing in coastal regions of Kenya.",
                "icd_code": "A90"
            },
            {
                "name": "Viral Hepatitis",
                "description": "Inflammation of the liver caused by viruses. Types A, B, and C are present in Kenya with varying prevalence.",
                "icd_code": "B15-B19"
            },
            {
                "name": "Tetanus",
                "description": "A serious bacterial disease affecting the nervous system. Maternal and neonatal tetanus remains a concern in some areas.",
                "icd_code": "A35"
            },
            {
                "name": "Hookworm Infection",
                "description": "An intestinal parasitic infection causing anemia and malnutrition. Common in rural areas with poor sanitation.",
                "icd_code": "B76"
            },
            {
                "name": "Influenza",
                "description": "A highly contagious viral respiratory infection with seasonal patterns in Kenya.",
                "icd_code": "J09-J11"
            },
            {
                "name": "Rabies",
                "description": "A viral disease transmitted through animal bites, particularly dogs. Fatal once symptoms appear but preventable through vaccination.",
                "icd_code": "A82"
            },
            
            # Non-communicable Diseases
            {
                "name": "Hypertension",
                "description": "High blood pressure, a major risk factor for cardiovascular diseases. Prevalence is increasing in urban areas of Kenya.",
                "icd_code": "I10-I15"
            },
            {
                "name": "Diabetes Mellitus",
                "description": "A metabolic disorder characterized by high blood sugar levels. Type 2 diabetes is increasing in Kenya due to lifestyle changes.",
                "icd_code": "E10-E14"
            },
            {
                "name": "Coronary Heart Disease",
                "description": "A condition where the heart's blood supply is blocked or interrupted by a build-up of fatty substances. Increasing in urban Kenya.",
                "icd_code": "I20-I25"
            },
            {
                "name": "Stroke",
                "description": "A serious life-threatening condition that occurs when blood supply to part of the brain is cut off. Increasing in Kenya with urbanization.",
                "icd_code": "I60-I69"
            },
            {
                "name": "Chronic Kidney Disease",
                "description": "A gradual loss of kidney function, often associated with diabetes and hypertension. Increasing in prevalence in Kenya.",
                "icd_code": "N18"
            },
            {
                "name": "Asthma",
                "description": "A chronic condition affecting the airways, causing breathing difficulties. Increasing in urban areas of Kenya.",
                "icd_code": "J45"
            },
            {
                "name": "Chronic Obstructive Pulmonary Disease",
                "description": "A group of lung conditions causing breathing difficulties. Associated with tobacco smoking and indoor air pollution in Kenya.",
                "icd_code": "J44"
            },
            {
                "name": "Rheumatic Heart Disease",
                "description": "Permanent damage to heart valves caused by rheumatic fever. Still common in Kenya due to inadequate treatment of streptococcal infections.",
                "icd_code": "I05-I09"
            },
            {
                "name": "Sickle Cell Disease",
                "description": "An inherited blood disorder affecting hemoglobin. Common in parts of western Kenya where malaria is endemic.",
                "icd_code": "D57"
            },
            {
                "name": "Peptic Ulcer Disease",
                "description": "Open sores that develop on the lining of the stomach or duodenum. Common in Kenya and often associated with H. pylori infection.",
                "icd_code": "K25-K28"
            },
            
            # Cancers
            {
                "name": "Cervical Cancer",
                "description": "A cancer arising from the cervix, often due to HPV infection. One of the most common cancers among women in Kenya.",
                "icd_code": "C53"
            },
            {
                "name": "Breast Cancer",
                "description": "Cancer that forms in the cells of the breasts. Increasing in prevalence among Kenyan women.",
                "icd_code": "C50"
            },
            {
                "name": "Prostate Cancer",
                "description": "Cancer of the prostate gland. The most common cancer among men in Kenya.",
                "icd_code": "C61"
            },
            {
                "name": "Esophageal Cancer",
                "description": "Cancer of the esophagus. Unusually high rates are found in parts of western Kenya.",
                "icd_code": "C15"
            },
            {
                "name": "Colorectal Cancer",
                "description": "Cancer of the colon or rectum. Increasing in Kenya with changing dietary patterns.",
                "icd_code": "C18-C20"
            },
            {
                "name": "Liver Cancer",
                "description": "Primary liver cancer, often associated with hepatitis B and C infections. Common in Kenya due to high prevalence of viral hepatitis.",
                "icd_code": "C22"
            },
            {
                "name": "Kaposi's Sarcoma",
                "description": "A cancer that forms in the lining of blood and lymph vessels. Often associated with HIV/AIDS in Kenya.",
                "icd_code": "C46"
            },
            {
                "name": "Stomach Cancer",
                "description": "Cancer that begins in the stomach. Associated with H. pylori infection, which is common in Kenya.",
                "icd_code": "C16"
            },
            {
                "name": "Lymphoma",
                "description": "Cancer of the lymphatic system. Burkitt lymphoma is particularly associated with malaria and Epstein-Barr virus in Kenya.",
                "icd_code": "C81-C85"
            },
            {
                "name": "Leukemia",
                "description": "Cancer of blood-forming tissues. Increasing in diagnosis as healthcare access improves in Kenya.",
                "icd_code": "C91-C95"
            },
            
            # Mental Health Conditions
            {
                "name": "Depression",
                "description": "A mental health disorder characterized by persistently depressed mood and loss of interest in activities. Increasingly recognized in Kenya.",
                "icd_code": "F32-F33"
            },
            {
                "name": "Anxiety Disorders",
                "description": "A group of mental health disorders characterized by feelings of anxiety and fear. Underdiagnosed but common in Kenya.",
                "icd_code": "F40-F41"
            },
            {
                "name": "Post-Traumatic Stress Disorder",
                "description": "A mental health condition triggered by experiencing or witnessing a terrifying event. Common in regions affected by conflict.",
                "icd_code": "F43.1"
            },
            {
                "name": "Schizophrenia",
                "description": "A chronic brain disorder affecting how a person thinks, feels, and behaves. Often undertreated due to limited mental health services in Kenya.",
                "icd_code": "F20"
            },
            {
                "name": "Bipolar Disorder",
                "description": "A mental disorder causing unusual shifts in mood, energy, activity levels, and concentration. Underdiagnosed in Kenya.",
                "icd_code": "F31"
            },
            {
                "name": "Alcohol Use Disorder",
                "description": "Problematic pattern of alcohol use leading to clinically significant impairment or distress. A growing concern in urban and rural Kenya.",
                "icd_code": "F10"
            },
            {
                "name": "Substance Use Disorders",
                "description": "Conditions involving the use of substances like khat, cannabis, and opioids. An increasing public health concern in Kenya.",
                "icd_code": "F11-F19"
            },
            {
                "name": "Epilepsy",
                "description": "A neurological disorder marked by recurrent seizures. Often stigmatized in Kenya and associated with mental health issues.",
                "icd_code": "G40"
            },
            
            # Nutritional Disorders
            {
                "name": "Protein-Energy Malnutrition",
                "description": "A form of malnutrition resulting from inadequate protein and energy intake. Still common in drought-affected areas of Kenya.",
                "icd_code": "E40-E46"
            },
            {
                "name": "Iron Deficiency Anemia",
                "description": "A condition where blood lacks adequate healthy red blood cells due to insufficient iron. Common among women and children in Kenya.",
                "icd_code": "D50"
            },
            {
                "name": "Vitamin A Deficiency",
                "description": "A lack of vitamin A in the diet, leading to night blindness and increased susceptibility to infections. Still reported in some regions of Kenya.",
                "icd_code": "E50"
            },
            {
                "name": "Obesity",
                "description": "A complex disease involving an excessive amount of body fat. Rising rapidly in urban areas of Kenya.",
                "icd_code": "E66"
            },
            {
                "name": "Iodine Deficiency Disorders",
                "description": "Disorders resulting from insufficient iodine in the diet, affecting thyroid function and development. Common in inland areas away from coastal regions.",
                "icd_code": "E00-E02"
            },
            
            # Other Conditions
            {
                "name": "Jigger Infestation (Tungiasis)",
                "description": "Parasitic skin disease caused by the female sand flea. Still endemic in rural poor communities in Kenya.",
                "icd_code": "B88.1"
            },
            {
                "name": "Podoconiosis",
                "description": "A non-infectious form of elephantiasis caused by prolonged exposure to irritant soil. Found in highland areas of Kenya.",
                "icd_code": "E88.8"
            },
            {
                "name": "Fluorosis",
                "description": "A condition caused by excessive fluoride intake, affecting teeth and bones. Common in parts of the Rift Valley with high fluoride in groundwater.",
                "icd_code": "K00.3"
            },
            {
                "name": "Sickle Cell Anemia",
                "description": "An inherited blood disorder where red blood cells become rigid and sticky. Prevalent in western Kenya as a protection against malaria.",
                "icd_code": "D57.1"
            },
            {
                "name": "Glaucoma",
                "description": "A group of eye conditions that damage the optic nerve. Higher prevalence among Kenyan populations of African descent.",
                "icd_code": "H40"
            },
            {
                "name": "Cataract",
                "description": "Clouding of the normally clear lens of the eye. A leading cause of blindness in Kenya, particularly in older adults.",
                "icd_code": "H25-H26"
            },
            {
                "name": "Onchocerciasis (River Blindness)",
                "description": "A parasitic disease caused by the filarial worm transmitted by blackflies. Present in western Kenya near Lake Victoria.",
                "icd_code": "B73"
            },
            {
                "name": "Rickets",
                "description": "A condition that results in weak or soft bones in children. Still seen in urban informal settlements in Kenya.",
                "icd_code": "E55.0"
            },
            {
                "name": "Rheumatoid Arthritis",
                "description": "An inflammatory disease that affects joints. Increasing diagnosis in Kenya with better access to healthcare.",
                "icd_code": "M05-M06"
            },
            {
                "name": "Osteoarthritis",
                "description": "A degenerative joint disease affecting joint cartilage and bones. Increasing in Kenya with aging population.",
                "icd_code": "M15-M19"
            },
            {
                "name": "Kala-azar (Visceral Leishmaniasis)",
                "description": "A parasitic disease affecting internal organs, characterized by fever, weight loss, and anemia. Endemic in parts of Eastern Kenya.",
                "icd_code": "B55.0"
            },
            {
                "name": "Yellow Fever",
                "description": "A viral disease transmitted by infected mosquitoes. Risk in forested areas of western Kenya.",
                "icd_code": "A95"
            },
            {
                "name": "Dracunculiasis (Guinea Worm Disease)",
                "description": "A parasitic disease caused by the guinea worm. Kenya has been certified free of transmission but remains vigilant.",
                "icd_code": "B72"
            },
            {
                "name": "Ebola Virus Disease",
                "description": "A rare but severe, often fatal illness in humans. Kenya has had no cases but maintains preparedness due to outbreaks in neighboring countries.",
                "icd_code": "A98.4"
            },
            {
                "name": "Plague",
                "description": "A serious bacterial infection transmitted by fleas. Rare in Kenya but surveillance is maintained.",
                "icd_code": "A20"
            },
            {
                "name": "African Trypanosomiasis (Sleeping Sickness)",
                "description": "A parasitic disease transmitted by the tsetse fly. Present in western parts of Kenya.",
                "icd_code": "B56"
            },
            {
                "name": "Chikungunya",
                "description": "A viral disease transmitted by infected mosquitoes, causing fever and joint pain. Outbreaks occur in coastal Kenya.",
                "icd_code": "A92.0"
            },
            {
                "name": "Filariasis",
                "description": "A parasitic disease caused by thread-like filarial worms. Coastal Kenya has been endemic for lymphatic filariasis.",
                "icd_code": "B74"
            },
            {
                "name": "Buruli Ulcer",
                "description": "A chronic debilitating skin and soft tissue infection. Reported in western Kenya near Lake Victoria.",
                "icd_code": "A31.1"
            },
            {
                "name": "Anthrax",
                "description": "A serious infectious disease caused by Bacillus anthracis bacteria. Occasional outbreaks occur in livestock-keeping communities.",
                "icd_code": "A22"
            },
            {
                "name": "Rift Valley Fever",
                "description": "A viral zoonosis affecting animals and humans. Periodic outbreaks occur in Kenya, particularly after heavy rainfall.",
                "icd_code": "A92.4"
            },
            {
                "name": "Leptospirosis",
                "description": "A bacterial infection spread through animal urine. Common in flood-prone areas and urban informal settlements.",
                "icd_code": "A27"
            },
            {
                "name": "Crimean-Congo Hemorrhagic Fever",
                "description": "A viral hemorrhagic fever transmitted by ticks. Sporadic cases occur in northeastern Kenya.",
                "icd_code": "A98.0"
            },
            {
                "name": "Poliomyelitis",
                "description": "A highly infectious viral disease that can cause permanent paralysis. Kenya has made significant progress towards eradication.",
                "icd_code": "A80"
            },
            {
                "name": "Diphtheria",
                "description": "A serious bacterial infection affecting the mucous membranes of the nose and throat. Vaccination has reduced incidence in Kenya.",
                "icd_code": "A36"
            },
            {
                "name": "Pertussis (Whooping Cough)",
                "description": "A highly contagious respiratory tract infection. Outbreaks still occur in under-vaccinated communities in Kenya.",
                "icd_code": "A37"
            },
            {
                "name": "Mumps",
                "description": "A viral infection that primarily affects saliva-producing glands. Still occurs in Kenya despite vaccination programs.",
                "icd_code": "B26"
            },
            {
                "name": "Rubella",
                "description": "A contagious viral infection identified by its characteristic red rash. Kenya is working towards elimination.",
                "icd_code": "B06"
            },
            {
                "name": "Chickenpox",
                "description": "A highly contagious viral infection causing an itchy rash with fluid-filled blisters. Common in childhood in Kenya.",
                "icd_code": "B01"
            },
            {
                "name": "Acute Respiratory Infections",
                "description": "Infections that affect the sinuses, throat, airways or lungs. A leading cause of morbidity in Kenya.",
                "icd_code": "J00-J06"
            },
            {
                "name": "Otitis Media",
                "description": "Inflammation or infection of the middle ear. Common in children in Kenya.",
                "icd_code": "H65-H66"
            },
            {
                "name": "Conjunctivitis",
                "description": "Inflammation or infection of the transparent membrane that lines the eyelid. Common in Kenya, especially during dry seasons.",
                "icd_code": "H10"
            },
            {
                "name": "Urinary Tract Infections",
                "description": "Infections affecting any part of the urinary system. Common in Kenya, particularly among women.",
                "icd_code": "N39.0"
            },
            {
                "name": "Gastroenteritis",
                "description": "Inflammation of the stomach and intestines. A common cause of diarrheal disease in Kenya.",
                "icd_code": "A09"
            },
            {
                "name": "Cellulitis",
                "description": "A common bacterial skin infection. Often seen in Kenya, particularly with poor wound care.",
                "icd_code": "L03"
            },
            {
                "name": "Impetigo",
                "description": "A highly contagious skin infection. Common among children in crowded living conditions in Kenya.",
                "icd_code": "L01"
            },
            {
                "name": "Tinea (Ringworm)",
                "description": "A fungal infection affecting the skin, scalp, or nails. Common in hot, humid conditions in Kenya.",
                "icd_code": "B35"
            },
            {
                "name": "Scabies",
                "description": "A contagious skin infestation by the human itch mite. Outbreaks occur in crowded living conditions in Kenya.",
                "icd_code": "B86"
            },
            {
                "name": "Ascariasis",
                "description": "An intestinal infection caused by the parasitic roundworm Ascaris lumbricoides. Common in areas with poor sanitation in Kenya.",
                "icd_code": "B77"
            },
            {
                "name": "Trichuriasis",
                "description": "An infection of the large intestine caused by the parasitic whipworm Trichuris trichiura. Common in rural Kenya.",
                "icd_code": "B79"
            },
            {
                "name": "Strongyloidiasis",
                "description": "An infection with the parasitic threadworm Strongyloides stercoralis. Found in areas with poor sanitation in Kenya.",
                "icd_code": "B78"
            },
            {
                "name": "Echinococcosis",
                "description": "A parasitic disease caused by tapeworms of the Echinococcus type. Occurs in pastoral communities in Kenya.",
                "icd_code": "B67"
            },
            {
                "name": "Cysticercosis",
                "description": "A tissue infection caused by the larval cysts of the pork tapeworm. Found in pig-keeping communities in Kenya.",
                "icd_code": "B69"
            },
            {
                "name": "Hydatid Disease",
                "description": "An infection caused by the larval stage of the tapeworm Echinococcus granulosus. Found in pastoral communities in Kenya.",
                "icd_code": "B67.0-B67.4"
            },
            {
                "name": "Taeniasis",
                "description": "An intestinal infection caused by adult tapeworms. Associated with consumption of undercooked meat in Kenya.",
                "icd_code": "B68"
            },
            {
                "name": "COVID-19",
                "description": "A respiratory illness caused by the SARS-CoV-2 virus. Kenya experienced multiple waves of the pandemic since 2020.",
                "icd_code": "U07.1"
            },
            {
                "name": "Marburg Virus Disease",
                "description": "A rare but severe hemorrhagic fever caused by Marburg virus. Kenya has experienced sporadic cases.",
                "icd_code": "A98.3"
            },
            {
                "name": "Mpox (Monkeypox)",
                "description": "A viral zoonotic disease causing fever and skin lesions. Sporadic cases have been reported in Kenya.",
                "icd_code": "B04"
            },
            {
                "name": "Lead Poisoning",
                "description": "Toxic condition resulting from the ingestion or inhalation of lead. Occurs in areas with informal mining and recycling in Kenya.",
                "icd_code": "T56.0"
            }
        ]
        
        # Counter for created diseases
        count = 0
        
        # Create diseases in the database
        for disease_data in diseases_data:
            try:
                disease = Disease.objects.create(
                    name=disease_data["name"],
                    description=disease_data["description"],
                    icd_code=disease_data["icd_code"]
                )
                count += 1
                self.stdout.write(f"Created disease: {disease.name} (ICD: {disease.icd_code})")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to create disease {disease_data['name']}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} diseases common in Kenya"))