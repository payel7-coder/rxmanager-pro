from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import *
from .serializers import *
from .permissions import get_doctor_for_user, IsDoctorOnly, IsDoctorOrAssistantDataEntry
from datetime import date, timedelta


# ============================================================
#  DOCTOR PROFILE — doctor-only (their own profile, edit only)
# ============================================================
class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsDoctorOnly]

    def get_queryset(self):
        # A doctor can only ever see/edit their own row.
        return Doctor.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def primary(self, request):
        """Used by both roles to render the clinic header — read-only lookup."""
        doctor = get_doctor_for_user(request.user)
        if doctor:
            return Response(DoctorSerializer(doctor).data)
        return Response({'detail': 'No doctor configured'}, status=404)


# ============================================================
#  PATIENTS — doctor + assistant (data entry allowed for both)
# ============================================================
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrAssistantDataEntry]

    def get_queryset(self):
        doctor = get_doctor_for_user(self.request.user)
        qs = Patient.objects.filter(doctor=doctor).order_by('-created_at')
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(patient_id__icontains=search) | Q(phone__icontains=search))
        return qs

    def perform_create(self, serializer):
        serializer.save(doctor=get_doctor_for_user(self.request.user))

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsDoctorOnly])
    def prescriptions(self, request, pk=None):
        # Viewing Rx history is a doctor-only privilege (assistants do data entry only).
        patient = self.get_object()
        prescriptions = patient.prescriptions.all().order_by('-visit_date')
        return Response(PrescriptionSerializer(prescriptions, many=True).data)


# ============================================================
#  MEDICINES — doctor + assistant (data entry allowed for both)
# ============================================================
class MedicineViewSet(viewsets.ModelViewSet):
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrAssistantDataEntry]

    def get_queryset(self):
        # Medicine catalogue is shared globally (not per-doctor) — same as a real drug database.
        qs = Medicine.objects.all().order_by('name')
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(generic_name__icontains=search))
        return qs


# ============================================================
#  TEMPLATES — doctor-only
# ============================================================
class PrescriptionTemplateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDoctorOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PrescriptionTemplateWriteSerializer
        return PrescriptionTemplateSerializer

    def get_queryset(self):
        doctor = get_doctor_for_user(self.request.user)
        qs = PrescriptionTemplate.objects.filter(doctor=doctor, is_active=True).order_by('-usage_count', 'name')
        search = self.request.query_params.get('search', '')
        disease = self.request.query_params.get('disease', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(disease__icontains=search))
        if disease:
            qs = qs.filter(disease__icontains=disease)
        return qs

    def perform_create(self, serializer):
        serializer.save(doctor=get_doctor_for_user(self.request.user))

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
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
        doctor = get_doctor_for_user(self.request.user)
        diseases = PrescriptionTemplate.objects.filter(doctor=doctor, is_active=True).values_list('disease', flat=True).distinct()
        return Response(sorted(set(d.strip() for d in diseases if d)))


# ============================================================
#  PRESCRIPTIONS — doctor-only
# ============================================================
class PrescriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDoctorOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PrescriptionWriteSerializer
        return PrescriptionSerializer

    def get_queryset(self):
        doctor = get_doctor_for_user(self.request.user)
        qs = Prescription.objects.filter(doctor=doctor).order_by('-visit_date', '-created_at')
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(Q(prescription_no__icontains=search) | Q(patient__name__icontains=search) | Q(diagnosis__icontains=search))
        return qs

    def perform_create(self, serializer):
        serializer.save(doctor=get_doctor_for_user(self.request.user))

    @action(detail=True, methods=['get'])
    def print_data(self, request, pk=None):
        prescription = self.get_object()
        return Response({
            'prescription': PrescriptionSerializer(prescription).data,
            'doctor': DoctorSerializer(prescription.doctor).data,
            'patient': PatientSerializer(prescription.patient).data,
        })


# ============================================================
#  DASHBOARD — doctor-only
# ============================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDoctorOnly])
def dashboard_stats(request):
    doctor = get_doctor_for_user(request.user)
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    return Response({
        'total_patients': Patient.objects.filter(doctor=doctor).count(),
        'total_prescriptions': Prescription.objects.filter(doctor=doctor).count(),
        'total_templates': PrescriptionTemplate.objects.filter(doctor=doctor, is_active=True).count(),
        'today_prescriptions': Prescription.objects.filter(doctor=doctor, visit_date=today).count(),
        'month_prescriptions': Prescription.objects.filter(doctor=doctor, visit_date__gte=thirty_days_ago).count(),
        'recent_patients': PatientSerializer(Patient.objects.filter(doctor=doctor).order_by('-created_at')[:5], many=True).data,
        'recent_prescriptions': PrescriptionSerializer(Prescription.objects.filter(doctor=doctor).order_by('-created_at')[:5], many=True).data,
    })
