import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rxmanager.settings')
django.setup()

from core.models import *

# Doctor
doc = Doctor.objects.create(
    name="Mohammed Rahman", qualification="MBBS, MD (Medicine)", specialization="General Medicine & Internal Medicine",
    registration_no="BMDC-12345", phone="+880-1711-000000", email="dr.rahman@clinic.com",
    clinic_name="Rahman Medical Center", clinic_address="House 12, Road 5, Dhanmondi, Dhaka-1205",
    clinic_phone="+880-2-9012345"
)

# Medicines
meds = [
    ("Napa", "Paracetamol", "Tablet", "500mg"),
    ("Moxacil", "Amoxicillin", "Capsule", "500mg"),
    ("Azimax", "Azithromycin", "Tablet", "500mg"),
    ("Fimoxyl", "Amoxicillin", "Syrup", "125mg/5ml"),
    ("Histacin", "Chlorpheniramine", "Tablet", "4mg"),
    ("Rantac", "Ranitidine", "Tablet", "150mg"),
    ("Seclo", "Omeprazole", "Capsule", "20mg"),
    ("Metformin", "Metformin HCl", "Tablet", "500mg"),
    ("Losartan", "Losartan Potassium", "Tablet", "50mg"),
    ("Atorvastatin", "Atorvastatin", "Tablet", "10mg"),
    ("Napa Extra", "Paracetamol + Caffeine", "Tablet", "500mg+65mg"),
    ("Vitamin C", "Ascorbic Acid", "Tablet", "500mg"),
    ("ORS", "Oral Rehydration Salt", "Powder", "1 sachet"),
    ("Fexo", "Fexofenadine", "Tablet", "120mg"),
    ("Montelukast", "Montelukast Sodium", "Tablet", "10mg"),
]
med_objs = {}
for name, generic, form, strength in meds:
    m = Medicine.objects.create(name=name, generic_name=generic, form=form, strength=strength)
    med_objs[name] = m

# Templates
t1 = PrescriptionTemplate.objects.create(
    doctor=doc, name="Common Cold & Fever", disease="Upper Respiratory Tract Infection",
    chief_complaint="Fever, runny nose, sore throat, body ache",
    diagnosis="URTI / Common Cold", advice="Take rest. Drink plenty of fluids. Avoid cold exposure.",
    follow_up_days=5, notes="If fever persists beyond 3 days, revisit."
)
TemplateMedicine.objects.create(template=t1, medicine=med_objs["Napa"], medicine_name="Napa 500mg", dose="1 tablet", frequency="Thrice daily", duration="5 days", timing="After Meal", order=0)
TemplateMedicine.objects.create(template=t1, medicine=med_objs["Histacin"], medicine_name="Histacin 4mg", dose="1 tablet", frequency="Twice daily", duration="5 days", timing="After Meal", order=1)
TemplateMedicine.objects.create(template=t1, medicine=med_objs["Vitamin C"], medicine_name="Vitamin C 500mg", dose="1 tablet", frequency="Once daily", duration="7 days", timing="After Meal", order=2)

t2 = PrescriptionTemplate.objects.create(
    doctor=doc, name="Bacterial Throat Infection", disease="Pharyngitis / Tonsillitis",
    chief_complaint="Severe sore throat, fever, difficulty swallowing",
    diagnosis="Acute Bacterial Pharyngitis", advice="Complete the full antibiotic course. Warm saline gargle twice daily.",
    follow_up_days=7
)
TemplateMedicine.objects.create(template=t2, medicine=med_objs["Azimax"], medicine_name="Azimax 500mg", dose="1 tablet", frequency="Once daily", duration="5 days", timing="Empty Stomach", order=0)
TemplateMedicine.objects.create(template=t2, medicine=med_objs["Napa"], medicine_name="Napa 500mg", dose="1 tablet", frequency="Thrice daily", duration="5 days", timing="After Meal", order=1)
TemplateMedicine.objects.create(template=t2, medicine=med_objs["Seclo"], medicine_name="Seclo 20mg", dose="1 capsule", frequency="Once daily", duration="5 days", timing="Before Meal", order=2)

t3 = PrescriptionTemplate.objects.create(
    doctor=doc, name="Hypertension Standard", disease="Hypertension",
    chief_complaint="Headache, dizziness, high blood pressure",
    diagnosis="Essential Hypertension", advice="Low salt diet. Regular walking 30 mins daily. Avoid stress. Monitor BP daily.",
    follow_up_days=30
)
TemplateMedicine.objects.create(template=t3, medicine=med_objs["Losartan"], medicine_name="Losartan 50mg", dose="1 tablet", frequency="Once daily", duration="Ongoing", timing="After Meal", order=0)
TemplateMedicine.objects.create(template=t3, medicine=med_objs["Atorvastatin"], medicine_name="Atorvastatin 10mg", dose="1 tablet", frequency="Once daily", duration="Ongoing", timing="At Bedtime", order=1)

t4 = PrescriptionTemplate.objects.create(
    doctor=doc, name="Type 2 Diabetes - Initial", disease="Type 2 Diabetes Mellitus",
    chief_complaint="Increased thirst, frequent urination, fatigue",
    diagnosis="Type 2 Diabetes Mellitus", advice="Diabetic diet - avoid sugar and refined carbs. Walk 30 mins daily. Check blood sugar weekly.",
    follow_up_days=14
)
TemplateMedicine.objects.create(template=t4, medicine=med_objs["Metformin"], medicine_name="Metformin 500mg", dose="1 tablet", frequency="Twice daily", duration="Ongoing", timing="After Meal", order=0)

t5 = PrescriptionTemplate.objects.create(
    doctor=doc, name="Gastritis / Acidity", disease="Gastritis / GERD",
    chief_complaint="Epigastric pain, heartburn, nausea",
    diagnosis="Acute Gastritis / Peptic Ulcer Disease", advice="Avoid spicy food, coffee, alcohol. Small frequent meals. Elevate head of bed.",
    follow_up_days=14
)
TemplateMedicine.objects.create(template=t5, medicine=med_objs["Seclo"], medicine_name="Seclo 20mg", dose="1 capsule", frequency="Twice daily", duration="14 days", timing="Before Meal", order=0)
TemplateMedicine.objects.create(template=t5, medicine=med_objs["Rantac"], medicine_name="Rantac 150mg", dose="1 tablet", frequency="Twice daily", duration="14 days", timing="Before Meal", order=1)

# Patients
patients_data = [
    ("Karim Hossain", 45, "M", "A+", "+880-1700-111111", "House 5, Mirpur, Dhaka", "Diabetes, Hypertension"),
    ("Fatima Begum", 32, "F", "B+", "+880-1800-222222", "Road 3, Gulshan, Dhaka", "None"),
    ("Rahim Uddin", 58, "M", "O+", "+880-1900-333333", "Uttara, Dhaka", "Hypertension"),
    ("Nasrin Akter", 28, "F", "A-", "+880-1600-444444", "Dhanmondi, Dhaka", "None"),
    ("Jamal Ahmed", 65, "M", "AB+", "+880-1500-555555", "Old Dhaka", "Diabetes, Arthritis"),
]
patient_objs = []
for name, age, gender, blood, phone, addr, history in patients_data:
    p = Patient.objects.create(name=name, age=age, gender=gender, blood_group=blood, phone=phone, address=addr, medical_history=history)
    patient_objs.append(p)

# Sample prescriptions
from django.utils import timezone
p1 = Prescription.objects.create(
    doctor=doc, patient=patient_objs[0], template=t4,
    diagnosis="Type 2 Diabetes Mellitus - Well controlled",
    blood_pressure="130/85", pulse="78", weight="72 kg",
    chief_complaint="Routine follow-up. Well controlled sugar levels.",
    advice="Continue current medication. Check HbA1c after 3 months.",
    follow_up_date=timezone.now().date().replace(day=min(timezone.now().day+30, 28))
)
PrescriptionMedicine.objects.create(prescription=p1, medicine_name="Metformin 500mg", dose="1 tablet", frequency="Twice daily", duration="Ongoing", timing="After Meal", order=0)

print("✅ Seed data created successfully!")
print(f"   Doctor: Dr. {doc.name}")
print(f"   Medicines: {Medicine.objects.count()}")
print(f"   Templates: {PrescriptionTemplate.objects.count()}")
print(f"   Patients: {Patient.objects.count()}")
