import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rxmanager.settings')
django.setup()
from django.contrib.auth.models import User
from core.models import *

# ===================== DOCTOR 1 (with login) =====================
user1 = User.objects.create_user(username='dr.rahman', password='doctor123')
doc1 = Doctor.objects.create(
    user=user1, name="Mohammed Rahman", qualification="MBBS, MD (Medicine)",
    specialization="General Medicine & Internal Medicine",
    registration_no="BMDC-12345", phone="+880-1711-000000",
    email="dr.rahman@clinic.com", clinic_name="Rahman Medical Center",
    clinic_address="House 12, Road 5, Dhanmondi, Dhaka-1205",
    clinic_phone="+880-2-9012345"
)

# Assistant for Doctor 1 (with login)
asst_user1 = User.objects.create_user(username='asst.rahim', password='assistant123')
asst1 = Assistant.objects.create(user=asst_user1, doctor=doc1, name="Rahim Sheikh", phone="+880-1722-000111")

# ===================== DOCTOR 2 (separate clinic — proves isolation) =====================
user2 = User.objects.create_user(username='dr.sultana', password='doctor123')
doc2 = Doctor.objects.create(
    user=user2, name="Nasreen Sultana", qualification="MBBS, FCPS (Gynae & Obs)",
    specialization="Gynecology & Obstetrics",
    registration_no="BMDC-67890", phone="+880-1811-222333",
    email="dr.sultana@clinic.com", clinic_name="Sultana Women's Care",
    clinic_address="Plot 7, Road 11, Banani, Dhaka-1213",
    clinic_phone="+880-2-8834567"
)

# ===================== MEDICINES (shared catalogue across all doctors) =====================
meds_data = [
    ("Napa","Paracetamol","Tablet","500mg","1 tablet","Thrice daily","5 days","After Meal"),
    ("Napa Extra","Paracetamol+Caffeine","Tablet","500mg+65mg","1 tablet","Thrice daily","5 days","After Meal"),
    ("Moxacil","Amoxicillin","Capsule","500mg","1 capsule","Thrice daily","7 days","After Meal"),
    ("Azimax","Azithromycin","Tablet","500mg","1 tablet","Once daily","5 days","Empty Stomach"),
    ("Fimoxyl","Amoxicillin","Syrup","125mg/5ml","10ml","Thrice daily","7 days","After Meal"),
    ("Histacin","Chlorpheniramine","Tablet","4mg","1 tablet","Twice daily","5 days","After Meal"),
    ("Fexo","Fexofenadine","Tablet","120mg","1 tablet","Once daily","7 days","After Meal"),
    ("Rantac","Ranitidine","Tablet","150mg","1 tablet","Twice daily","14 days","Before Meal"),
    ("Seclo","Omeprazole","Capsule","20mg","1 capsule","Twice daily","14 days","Before Meal"),
    ("Metformin","Metformin HCl","Tablet","500mg","1 tablet","Twice daily","Ongoing","After Meal"),
    ("Losartan","Losartan Potassium","Tablet","50mg","1 tablet","Once daily","Ongoing","After Meal"),
    ("Atorvastatin","Atorvastatin","Tablet","10mg","1 tablet","Once daily","Ongoing","At Bedtime"),
    ("Vitamin C","Ascorbic Acid","Tablet","500mg","1 tablet","Once daily","30 days","After Meal"),
    ("Zinc","Zinc Sulfate","Tablet","20mg","1 tablet","Once daily","14 days","After Meal"),
    ("ORS","Oral Rehydration Salt","Powder","1 sachet","1 sachet","After each stool","3 days","As Needed"),
    ("Montelukast","Montelukast Sodium","Tablet","10mg","1 tablet","Once daily","14 days","At Bedtime"),
    ("Folic Acid","Folic Acid","Tablet","5mg","1 tablet","Once daily","90 days","After Meal"),
    ("Cetirizine","Cetirizine HCl","Tablet","10mg","1 tablet","Once daily","7 days","At Bedtime"),
    ("Pantoprazole","Pantoprazole","Tablet","40mg","1 tablet","Once daily","14 days","Before Meal"),
    ("Iron Sucrose","Iron Sucrose","Tablet","100mg","1 tablet","Once daily","60 days","After Meal"),
]
med_objs = {}
for name, generic, form, strength, dose, freq, dur, timing in meds_data:
    m = Medicine.objects.create(name=name, generic_name=generic, form=form, strength=strength,
        default_dose=dose, default_frequency=freq, default_duration=dur, default_timing=timing)
    med_objs[name] = m

# ===================== TEMPLATES for Doctor 1 =====================
t1 = PrescriptionTemplate.objects.create(doctor=doc1, name="Common Cold & Fever", disease="Upper Respiratory Tract Infection",
    chief_complaint="Fever, runny nose, sore throat, body ache", diagnosis="URTI / Common Cold",
    advice="Take rest. Drink plenty of fluids.", follow_up_days=5)
TemplateMedicine.objects.create(template=t1, medicine=med_objs["Napa"], medicine_name="Napa 500mg", dose="1 tablet", frequency="Thrice daily", duration="5 days", timing="After Meal", order=0)
TemplateMedicine.objects.create(template=t1, medicine=med_objs["Histacin"], medicine_name="Histacin 4mg", dose="1 tablet", frequency="Twice daily", duration="5 days", timing="After Meal", order=1)

t2 = PrescriptionTemplate.objects.create(doctor=doc1, name="Hypertension Standard", disease="Hypertension",
    chief_complaint="Headache, dizziness, high blood pressure", diagnosis="Essential Hypertension",
    advice="Low salt diet. Regular walking 30 mins daily.", follow_up_days=30)
TemplateMedicine.objects.create(template=t2, medicine=med_objs["Losartan"], medicine_name="Losartan 50mg", dose="1 tablet", frequency="Once daily", duration="Ongoing", timing="After Meal", order=0)

t3 = PrescriptionTemplate.objects.create(doctor=doc1, name="Type 2 Diabetes - Initial", disease="Type 2 Diabetes Mellitus",
    chief_complaint="Increased thirst, frequent urination, fatigue", diagnosis="Type 2 Diabetes Mellitus",
    advice="Diabetic diet. Walk 30 mins daily.", follow_up_days=14)
TemplateMedicine.objects.create(template=t3, medicine=med_objs["Metformin"], medicine_name="Metformin 500mg", dose="1 tablet", frequency="Twice daily", duration="Ongoing", timing="After Meal", order=0)

# ===================== TEMPLATE for Doctor 2 (proves data isolation) =====================
t4 = PrescriptionTemplate.objects.create(doctor=doc2, name="Antenatal Routine", disease="Pregnancy - Routine Checkup",
    chief_complaint="Routine antenatal visit", diagnosis="Normal Pregnancy - Routine ANC",
    advice="Continue iron and folic acid. Balanced diet. Adequate rest.", follow_up_days=28)
TemplateMedicine.objects.create(template=t4, medicine=med_objs["Iron Sucrose"], medicine_name="Iron Sucrose 100mg", dose="1 tablet", frequency="Once daily", duration="60 days", timing="After Meal", order=0)
TemplateMedicine.objects.create(template=t4, medicine=med_objs["Folic Acid"], medicine_name="Folic Acid 5mg", dose="1 tablet", frequency="Once daily", duration="90 days", timing="After Meal", order=1)

# ===================== PATIENTS for Doctor 1 =====================
for name, age, gender, blood, phone, addr, history in [
    ("Karim Hossain", 45, "M", "A+", "+880-1700-111111", "Mirpur, Dhaka", "Diabetes, Hypertension"),
    ("Fatima Begum",  32, "F", "B+", "+880-1800-222222", "Gulshan, Dhaka", "None"),
    ("Rahim Uddin",   58, "M", "O+", "+880-1900-333333", "Uttara, Dhaka", "Hypertension"),
]:
    Patient.objects.create(doctor=doc1, name=name, age=age, gender=gender, blood_group=blood, phone=phone, address=addr, medical_history=history)

# ===================== PATIENTS for Doctor 2 (proves isolation) =====================
for name, age, gender, blood, phone, addr, history in [
    ("Nasrin Akter", 28, "F", "A-", "+880-1600-444444", "Banani, Dhaka", "First pregnancy, 20 weeks"),
    ("Shirin Khan",  31, "F", "B-", "+880-1500-555555", "Baridhara, Dhaka", "Second pregnancy"),
]:
    Patient.objects.create(doctor=doc2, name=name, age=age, gender=gender, blood_group=blood, phone=phone, address=addr, medical_history=history)

print("✅ Seed data created!")
print()
print("===== LOGIN CREDENTIALS =====")
print("Doctor 1:    username=dr.rahman      password=doctor123     (Rahman Medical Center)")
print("Assistant 1: username=asst.rahim     password=assistant123  (works for Dr. Rahman)")
print("Doctor 2:    username=dr.sultana     password=doctor123     (Sultana Women's Care)")
print()
print(f"Medicines: {Medicine.objects.count()}")
print(f"Doctor 1 -> Patients: {Patient.objects.filter(doctor=doc1).count()}, Templates: {PrescriptionTemplate.objects.filter(doctor=doc1).count()}")
print(f"Doctor 2 -> Patients: {Patient.objects.filter(doctor=doc2).count()}, Templates: {PrescriptionTemplate.objects.filter(doctor=doc2).count()}")
