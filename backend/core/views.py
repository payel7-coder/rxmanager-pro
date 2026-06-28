from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Q
from django.http import HttpResponse
from .models import *
from .serializers import *
import json
from datetime import datetime, date, timedelta


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    @action(detail=False, methods=['get'])
    def primary(self, request):
        doctor = Doctor.objects.first()
        if doctor:
            return Response(DoctorSerializer(doctor).data)
        return Response({'detail': 'No doctor configured'}, status=404)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientSerializer

    def get_queryset(self):
        qs = Patient.objects.all().order_by('-created_at')
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(patient_id__icontains=search) |
                Q(phone__icontains=search)
            )
        return qs

    @action(detail=True, methods=['get'])
    def prescriptions(self, request, pk=None):
        patient = self.get_object()
        prescriptions = patient.prescriptions.all().order_by('-visit_date')
        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data)


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all().order_by('name')
    serializer_class = MedicineSerializer

    def get_queryset(self):
        qs = Medicine.objects.all().order_by('name')
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(generic_name__icontains=search))
        return qs


class PrescriptionTemplateViewSet(viewsets.ModelViewSet):
    queryset = PrescriptionTemplate.objects.filter(is_active=True).order_by('-usage_count', 'name')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PrescriptionTemplateWriteSerializer
        return PrescriptionTemplateSerializer

    def get_queryset(self):
        qs = PrescriptionTemplate.objects.filter(is_active=True).order_by('-usage_count', 'name')
        search = self.request.query_params.get('search', '')
        disease = self.request.query_params.get('disease', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(disease__icontains=search))
        if disease:
            qs = qs.filter(disease__icontains=disease)
        return qs

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """Clone a template without modifying the original"""
        template = self.get_object()
        medicines = list(template.medicines.all())
        
        template.pk = None
        template.name = f"{template.name} (Copy)"
        template.usage_count = 0
        template.save()
        
        for med in medicines:
            med.pk = None
            med.template = template
            med.save()
        
        return Response(PrescriptionTemplateSerializer(template).data, status=201)

    @action(detail=False, methods=['get'])
    def diseases(self, request):
        diseases = PrescriptionTemplate.objects.filter(is_active=True).values_list('disease', flat=True).distinct()
        return Response(sorted(set(d.strip() for d in diseases if d)))


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all().order_by('-visit_date', '-created_at')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PrescriptionWriteSerializer
        return PrescriptionSerializer

    def get_queryset(self):
        qs = Prescription.objects.all().order_by('-visit_date', '-created_at')
        patient = self.request.query_params.get('patient', '')
        search = self.request.query_params.get('search', '')
        date_from = self.request.query_params.get('date_from', '')
        date_to = self.request.query_params.get('date_to', '')
        
        if patient:
            qs = qs.filter(patient__id=patient)
        if search:
            qs = qs.filter(
                Q(prescription_no__icontains=search) |
                Q(patient__name__icontains=search) |
                Q(diagnosis__icontains=search)
            )
        if date_from:
            qs = qs.filter(visit_date__gte=date_from)
        if date_to:
            qs = qs.filter(visit_date__lte=date_to)
        return qs

    @action(detail=True, methods=['get'])
    def print_data(self, request, pk=None):
        """Get all data needed for print view"""
        prescription = self.get_object()
        doctor = prescription.doctor
        patient = prescription.patient
        
        data = {
            'prescription': PrescriptionSerializer(prescription).data,
            'doctor': DoctorSerializer(doctor).data,
            'patient': PatientSerializer(patient).data,
        }
        return Response(data)


@api_view(['GET'])
def dashboard_stats(request):
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    
    stats = {
        'total_patients': Patient.objects.count(),
        'total_prescriptions': Prescription.objects.count(),
        'total_templates': PrescriptionTemplate.objects.filter(is_active=True).count(),
        'today_prescriptions': Prescription.objects.filter(visit_date=today).count(),
        'month_prescriptions': Prescription.objects.filter(visit_date__gte=thirty_days_ago).count(),
        'recent_patients': PatientSerializer(
            Patient.objects.order_by('-created_at')[:5], many=True
        ).data,
        'recent_prescriptions': PrescriptionSerializer(
            Prescription.objects.order_by('-created_at')[:5], many=True
        ).data,
    }
    return Response(stats)
