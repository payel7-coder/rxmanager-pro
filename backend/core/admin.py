from django.contrib import admin
from .models import (
    Doctor, Assistant, Patient, Medicine,
    PrescriptionTemplate, TemplateMedicine,
    Prescription, PrescriptionMedicine
)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'registration_no', 'clinic_name', 'user']
    search_fields = ['name', 'registration_no', 'clinic_name']


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = ['name', 'doctor', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'doctor']
    search_fields = ['name']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'name', 'doctor', 'age', 'gender', 'blood_group', 'phone']
    list_filter = ['doctor', 'gender', 'blood_group']
    search_fields = ['name', 'patient_id', 'phone']


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'form', 'strength', 'manufacturer']
    list_filter = ['form']
    search_fields = ['name', 'generic_name']


class TemplateMedicineInline(admin.TabularInline):
    model = TemplateMedicine
    extra = 1


@admin.register(PrescriptionTemplate)
class PrescriptionTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'disease', 'doctor', 'usage_count', 'is_active']
    list_filter = ['doctor', 'is_active']
    search_fields = ['name', 'disease']
    inlines = [TemplateMedicineInline]


class PrescriptionMedicineInline(admin.TabularInline):
    model = PrescriptionMedicine
    extra = 0


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_no', 'patient', 'doctor', 'visit_date', 'status']
    list_filter = ['doctor', 'status', 'visit_date']
    search_fields = ['prescription_no', 'patient__name', 'diagnosis']
    inlines = [PrescriptionMedicineInline]
