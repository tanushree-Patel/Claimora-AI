
import asyncio

from sqlalchemy import select

from app.db.models import IndianMedicalCode
from app.db.session import AsyncSessionLocal

# A real sample of 50 ICD-10 and SNOMED-CT entries commonly used in Indian health claims
SEED_CODES = [
    # ICD-10 Diagnosis Codes
    {"code_system": "ICD-10", "code": "I10", "display_name": "Essential (primary) hypertension", "description": "High blood pressure without an identifiable secondary cause"},
    {"code_system": "ICD-10", "code": "I11.9", "display_name": "Hypertensive heart disease without heart failure", "description": "Heart disease caused by high blood pressure without heart failure"},
    {"code_system": "ICD-10", "code": "E11.9", "display_name": "Type 2 diabetes mellitus without complications", "description": "Non-insulin dependent diabetes mellitus without secondary complications"},
    {"code_system": "ICD-10", "code": "E11.65", "display_name": "Type 2 diabetes mellitus with hyperglycemia", "description": "Type 2 diabetes mellitus uncontrolled with elevated blood sugar levels"},
    {"code_system": "ICD-10", "code": "J45.909", "display_name": "Unspecified asthma, uncomplicated", "description": "Chronic inflammatory disease of the airways resulting in breathing difficulty"},
    {"code_system": "ICD-10", "code": "K21.9", "display_name": "Gastro-esophageal reflux disease without esophagitis", "description": "GERD causing heartburn without visible inflammation in esophagus"},
    {"code_system": "ICD-10", "code": "A90", "display_name": "Dengue fever [classical dengue]", "description": "Mosquito-borne viral disease causing high fever and severe flu-like illness"},
    {"code_system": "ICD-10", "code": "A01.0", "display_name": "Typhoid fever", "description": "Bacterial infection caused by Salmonella typhi"},
    {"code_system": "ICD-10", "code": "K35.80", "display_name": "Unspecified acute appendicitis", "description": "Acute inflammation of the appendix requiring surgical intervention"},
    {"code_system": "ICD-10", "code": "H26.9", "display_name": "Unspecified cataract", "description": "Clouding of the lens in the eye affecting vision"},
    {"code_system": "ICD-10", "code": "M17.9", "display_name": "Osteoarthritis of knee, unspecified", "description": "Degenerative joint disease of the knee causing pain and stiffness"},
    {"code_system": "ICD-10", "code": "U07.1", "display_name": "COVID-19", "description": "Acute respiratory disease caused by severe acute respiratory syndrome coronavirus 2"},
    {"code_system": "ICD-10", "code": "B50.9", "display_name": "Plasmodium falciparum malaria, unspecified", "description": "Severe malaria infection caused by Plasmodium falciparum parasite"},
    {"code_system": "ICD-10", "code": "N39.0", "display_name": "Urinary tract infection, site not specified", "description": "Bacterial infection affecting parts of the urinary system"},
    {"code_system": "ICD-10", "code": "I21.9", "display_name": "Acute myocardial infarction, unspecified", "description": "Heart attack caused by sudden lack of blood supply to heart muscle"},
    {"code_system": "ICD-10", "code": "I63.9", "display_name": "Cerebral infarction, unspecified", "description": "Ischemic stroke caused by interrupted blood flow to the brain"},
    {"code_system": "ICD-10", "code": "N18.9", "display_name": "Chronic kidney disease, unspecified", "description": "Gradual loss of kidney function over time"},
    {"code_system": "ICD-10", "code": "J18.9", "display_name": "Pneumonia, unspecified organism", "description": "Infection that inflames air sacs in one or both lungs"},
    {"code_system": "ICD-10", "code": "K80.20", "display_name": "Calculus of gallbladder without cholecystitis", "description": "Gallstones present in gallbladder without active inflammation"},
    {"code_system": "ICD-10", "code": "D64.9", "display_name": "Anemia, unspecified", "description": "Lack of adequate healthy red blood cells to carry oxygen"},
    {"code_system": "ICD-10", "code": "E03.9", "display_name": "Hypothyroidism, unspecified", "description": "Underactive thyroid gland producing insufficient thyroid hormones"},
    {"code_system": "ICD-10", "code": "G43.909", "display_name": "Migraine, unspecified, not intractable", "description": "Neurological condition causing severe recurring headaches"},
    {"code_system": "ICD-10", "code": "S72.009A", "display_name": "Fracture of head and neck of femur, initial encounter", "description": "Hip fracture common in elderly patients requiring orthopedic surgery"},
    {"code_system": "ICD-10", "code": "L30.9", "display_name": "Dermatitis, unspecified", "description": "Skin inflammation causing itchy, dry, or swollen skin"},
    {"code_system": "ICD-10", "code": "F32.9", "display_name": "Major depressive disorder, single episode, unspecified", "description": "Mood disorder causing persistent feelings of sadness and loss of interest"},
    {"code_system": "ICD-10", "code": "A15.0", "display_name": "Tuberculosis of lung", "description": "Infectious bacterial disease affecting lung parenchyma"},
    {"code_system": "ICD-10", "code": "K85.90", "display_name": "Acute pancreatitis, unspecified", "description": "Sudden inflammation of the pancreas requiring emergency medical care"},
    {"code_system": "ICD-10", "code": "J03.90", "display_name": "Acute tonsillitis, unspecified", "description": "Acute inflammation and infection of the palatine tonsils"},
    {"code_system": "ICD-10", "code": "N20.0", "display_name": "Calculus of kidney", "description": "Kidney stones causing acute renal colic and pain"},
    {"code_system": "ICD-10", "code": "K40.90", "display_name": "Unilateral inguinal hernia, without obstruction or gangrene", "description": "Protrusion of abdominal cavity tissue through inguinal canal"},
    {"code_system": "ICD-10", "code": "G40.909", "display_name": "Epilepsy, unspecified, not intractable", "description": "Central nervous system disorder characterized by recurrent seizures"},
    {"code_system": "ICD-10", "code": "R50.9", "display_name": "Fever, unspecified", "description": "Elevated body temperature of unknown origin"},
    {"code_system": "ICD-10", "code": "A09", "display_name": "Infectious gastroenteritis and colitis, unspecified", "description": "Acute intestinal infection causing diarrhea and vomiting"},
    {"code_system": "ICD-10", "code": "R10.9", "display_name": "Unspecified abdominal pain", "description": "Generalized or localized discomfort in abdominal region"},
    {"code_system": "ICD-10", "code": "M54.50", "display_name": "Low back pain, unspecified", "description": "Common lumbar spine discomfort or muscle strain"},

    # SNOMED-CT Clinical Terms & Concepts
    {"code_system": "SNOMED-CT", "code": "38341003", "display_name": "Hypertensive disorder", "description": "Systemic elevated arterial blood pressure"},
    {"code_system": "SNOMED-CT", "code": "44054006", "display_name": "Type 2 diabetes mellitus", "description": "Metabolic disorder characterized by hyperglycemia and insulin resistance"},
    {"code_system": "SNOMED-CT", "code": "195662009", "display_name": "Acute viral hepatitis", "description": "Acute inflammation of the liver caused by viral infection"},
    {"code_system": "SNOMED-CT", "code": "82271004", "display_name": "Dengue fever", "description": "Arboviral illness transmitted by Aedes mosquitoes"},
    {"code_system": "SNOMED-CT", "code": "64572001", "display_name": "Disease caused by 2019 novel coronavirus", "description": "Infection caused by SARS-CoV-2 coronavirus"},
    {"code_system": "SNOMED-CT", "code": "233604007", "display_name": "Pneumonia", "description": "Infectious disease of lung tissue"},
    {"code_system": "SNOMED-CT", "code": "13645005", "display_name": "Chronic obstructive lung disease", "description": "Progressive lung disease impairing airflow"},
    {"code_system": "SNOMED-CT", "code": "42343007", "display_name": "Congestive heart failure", "description": "Inability of heart muscle to pump blood efficiently"},
    {"code_system": "SNOMED-CT", "code": "254837009", "display_name": "Malignant neoplasm of breast", "description": "Cancer originating from breast tissue cells"},
    {"code_system": "SNOMED-CT", "code": "230690007", "display_name": "Cerebrovascular accident", "description": "Acute stroke due to vascular brain injury"},
    {"code_system": "SNOMED-CT", "code": "417357006", "display_name": "Acute appendicitis", "description": "Inflammation of the vermiform appendix"},
    {"code_system": "SNOMED-CT", "code": "235856003", "display_name": "Typhoid fever", "description": "Systemic infection with Salmonella enterica serovar Typhi"},
    {"code_system": "SNOMED-CT", "code": "312608009", "display_name": "Chronic kidney disease stage 5", "description": "End-stage renal disease requiring dialysis or transplantation"},
    {"code_system": "SNOMED-CT", "code": "91936005", "display_name": "Allergic rhinitis", "description": "Allergic inflammation of the nasal airways"},
    {"code_system": "SNOMED-CT", "code": "56717001", "display_name": "Tuberculosis", "description": "Mycobacterial infection affecting lungs or extra-pulmonary organs"},
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        existing = await session.execute(select(IndianMedicalCode.code))
        existing_codes = {row[0] for row in existing.all()}

        new_rows = [
            IndianMedicalCode(**item)
            for item in SEED_CODES
            if item["code"] not in existing_codes
        ]
        session.add_all(new_rows)
        await session.commit()
        print(f"Inserted {len(new_rows)} new codes. Total dataset target: {len(SEED_CODES)}.")


if __name__ == "__main__":
    asyncio.run(seed())