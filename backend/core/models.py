from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Doctor(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    name        = models.CharField(max_length=200)
    qualification  = models.CharField(max_length=300)
    specialization = models.CharField(max_length=200)
    registration_no = models.CharField(max_length=100, unique=True)
    phone       = models.CharField(max_length=20)
    email       = models.EmailField(blank=True)
    clinic_name    = models.CharField(max_length=200)
    clinic_address = models.TextField()
    clinic_phone   = models.CharField(max_length=20, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.name}"


class Assistant(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='assistant_profile')
    doctor  = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='assistants')
    name    = models.CharField(max_length=200)
    phone   = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Assistant of Dr. {self.doctor.name})"


class Patient(models.Model):
    GENDER_CHOICES = [('M','Male'),('F','Female'),('O','Other')]
    BLOOD_GROUP_CHOICES = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),('Unknown','Unknown'),
    ]
    doctor     = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patients')
    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    name       = models.CharField(max_length=200)
    age        = models.IntegerField()
    age_unit   = models.CharField(max_length=10, default='Years',
                   choices=[('Years','Years'),('Months','Months'),('Days','Days')])
    gender     = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='Unknown')
    phone      = models.CharField(max_length=20, blank=True)
    address    = models.TextField(blank=True)
    email      = models.EmailField(blank=True)
    allergies  = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last = Patient.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.patient_id = f"PT{next_id:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_id} - {self.name}"


class Medicine(models.Model):
    FORM_CHOICES = [
        ('Tablet','Tablet'),('Capsule','Capsule'),('Syrup','Syrup'),
        ('Injection','Injection'),('Cream','Cream'),('Drops','Drops'),
        ('Inhaler','Inhaler'),('Patch','Patch'),('Suppository','Suppository'),
        ('Powder','Powder'),('Gel','Gel'),('Ointment','Ointment'),
    ]
    TIMING_CHOICES = [
        ('Before Meal','Before Meal'),('After Meal','After Meal'),
        ('With Meal','With Meal'),('Empty Stomach','Empty Stomach'),
        ('At Bedtime','At Bedtime'),('As Needed','As Needed'),
    ]
    FREQUENCY_CHOICES = [
        ('Once daily','Once daily'),('Twice daily','Twice daily'),
        ('Thrice daily','Thrice daily'),('Four times daily','Four times daily'),
        ('Every 6 hours','Every 6 hours'),('Every 8 hours','Every 8 hours'),
        ('Every 12 hours','Every 12 hours'),('Weekly','Weekly'),('As needed','As needed'),
    ]
    name         = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    form         = models.CharField(max_length=20, choices=FORM_CHOICES)
    strength     = models.CharField(max_length=50, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    default_dose      = models.CharField(max_length=100, blank=True)
    default_frequency = models.CharField(max_length=30, choices=FREQUENCY_CHOICES, blank=True)
    default_duration  = models.CharField(max_length=50, blank=True)
    default_timing    = models.CharField(max_length=20, choices=TIMING_CHOICES, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} {self.strength} ({self.form})"


class PrescriptionTemplate(models.Model):
    doctor      = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='templates')
    name        = models.CharField(max_length=200)
    disease     = models.CharField(max_length=200)
    chief_complaint = models.TextField(blank=True)
    diagnosis   = models.TextField(blank=True)
    advice      = models.TextField(blank=True)
    follow_up_days = models.IntegerField(default=7)
    notes       = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.disease}"


class TemplateMedicine(models.Model):
    template     = models.ForeignKey(PrescriptionTemplate, on_delete=models.CASCADE, related_name='medicines')
    medicine     = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True)
    medicine_name = models.CharField(max_length=200)
    dose         = models.CharField(max_length=100)
    frequency    = models.CharField(max_length=30)
    duration     = models.CharField(max_length=50)
    timing       = models.CharField(max_length=20, default='After Meal')
    instructions = models.TextField(blank=True)
    order        = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']


class Prescription(models.Model):
    STATUS_CHOICES = [('Draft','Draft'),('Final','Final')]
    prescription_no = models.CharField(max_length=20, unique=True, editable=False)
    doctor      = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    patient     = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    template    = models.ForeignKey(PrescriptionTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    visit_date  = models.DateField(default=timezone.now)
    chief_complaint = models.TextField(blank=True)
    history        = models.TextField(blank=True)
    investigation  = models.TextField(blank=True)
    diagnosis      = models.TextField()
    blood_pressure = models.CharField(max_length=20, blank=True)
    temperature = models.CharField(max_length=20, blank=True)
    pulse       = models.CharField(max_length=20, blank=True)
    weight      = models.CharField(max_length=20, blank=True)
    advice      = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    notes       = models.TextField(blank=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Final')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.prescription_no:
            today = timezone.now().strftime('%Y%m%d')
            count = Prescription.objects.filter(created_at__date=timezone.now().date()).count() + 1
            self.prescription_no = f"RX{today}{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prescription_no} - {self.patient.name}"


class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=200)
    dose         = models.CharField(max_length=100)
    frequency    = models.CharField(max_length=30)
    duration     = models.CharField(max_length=50)
    timing       = models.CharField(max_length=20, default='After Meal')
    instructions = models.TextField(blank=True)
    order        = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
