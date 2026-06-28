from rest_framework import serializers
from .models import *


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    total_prescriptions = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['patient_id', 'created_at', 'updated_at']

    def get_total_prescriptions(self, obj):
        return obj.prescriptions.count()


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


class TemplateMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateMedicine
        fields = '__all__'
        read_only_fields = ['template']


class PrescriptionTemplateSerializer(serializers.ModelSerializer):
    medicines = TemplateMedicineSerializer(many=True, read_only=True)
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = PrescriptionTemplate
        fields = '__all__'

    def get_doctor_name(self, obj):
        return str(obj.doctor)


class PrescriptionTemplateWriteSerializer(serializers.ModelSerializer):
    medicines = TemplateMedicineSerializer(many=True)

    class Meta:
        model = PrescriptionTemplate
        fields = '__all__'

    def create(self, validated_data):
        medicines_data = validated_data.pop('medicines', [])
        template = PrescriptionTemplate.objects.create(**validated_data)
        for i, med in enumerate(medicines_data):
            med['order'] = i
            TemplateMedicine.objects.create(template=template, **med)
        return template

    def update(self, instance, validated_data):
        medicines_data = validated_data.pop('medicines', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.medicines.all().delete()
        for i, med in enumerate(medicines_data):
            med['order'] = i
            TemplateMedicine.objects.create(template=instance, **med)
        return instance


class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionMedicine
        fields = '__all__'
        read_only_fields = ['prescription']


class PrescriptionSerializer(serializers.ModelSerializer):
    medicines = PrescriptionMedicineSerializer(many=True, read_only=True)
    patient_name = serializers.SerializerMethodField()
    patient_age = serializers.SerializerMethodField()
    patient_gender = serializers.SerializerMethodField()
    patient_id_no = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = '__all__'

    def get_patient_name(self, obj):
        return obj.patient.name
    def get_patient_age(self, obj):
        return f"{obj.patient.age} {obj.patient.age_unit}"
    def get_patient_gender(self, obj):
        return obj.patient.get_gender_display()
    def get_patient_id_no(self, obj):
        return obj.patient.patient_id
    def get_doctor_name(self, obj):
        return str(obj.doctor)


class PrescriptionWriteSerializer(serializers.ModelSerializer):
    medicines = PrescriptionMedicineSerializer(many=True)

    class Meta:
        model = Prescription
        fields = '__all__'

    def create(self, validated_data):
        medicines_data = validated_data.pop('medicines', [])
        prescription = Prescription.objects.create(**validated_data)
        for i, med in enumerate(medicines_data):
            med['order'] = i
            PrescriptionMedicine.objects.create(prescription=prescription, **med)
        if prescription.template:
            prescription.template.usage_count += 1
            prescription.template.save()
        return prescription

    def update(self, instance, validated_data):
        medicines_data = validated_data.pop('medicines', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.medicines.all().delete()
        for i, med in enumerate(medicines_data):
            med['order'] = i
            PrescriptionMedicine.objects.create(prescription=instance, **med)
        return instance
