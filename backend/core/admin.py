from django.contrib import admin
from .models import Doctor, Patient, Medicine, PrescriptionTemplate, TemplateMedicine, Prescription, PrescriptionMedicine


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'registration_no', 'clinic_name']


class TemplateMedicineInline(admin.TabularInline):
    model = TemplateMedicine
    extra = 1


@admin.register(PrescriptionTemplate)
class PrescriptionTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'disease', 'doctor', 'usage_count', 'is_active']
    list_filter = ['is_active', 'disease']
    search_fields = ['name', 'disease']
    inlines = [TemplateMedicineInline]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'name', 'age', 'gender', 'blood_group', 'phone', 'created_at']
    search_fields = ['name', 'patient_id', 'phone']
    list_filter = ['gender', 'blood_group']


class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 0


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_no', 'patient', 'diagnosis', 'visit_date', 'status']
    search_fields = ['prescription_no', 'patient__name', 'diagnosis']
    list_filter = ['status', 'visit_date']
    inlines = [PrescriptionMedicineInline]


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'form', 'strength', 'manufacturer']
    search_fields = ['name', 'generic_name']
    list_filter = ['form']
