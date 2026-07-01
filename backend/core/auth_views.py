from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User

from .models import Doctor, Assistant
from .permissions import get_role, get_doctor_for_user, IsDoctorOnly
from .auth_serializers import (
    DoctorRegisterSerializer, AssistantCreateSerializer, AssistantSerializer, MeSerializer
)


# ---------- Custom JWT login: embeds role + doctor info in the response ----------
class RoleAwareTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        role = get_role(user)
        if role is None:
            from rest_framework import serializers as drf_serializers
            raise drf_serializers.ValidationError(
                "This account has no doctor or assistant profile attached."
            )
        doctor = get_doctor_for_user(user)
        data['role'] = role
        data['doctor_id'] = doctor.id
        data['doctor_name'] = doctor.name
        data['display_name'] = doctor.name if role == 'doctor' else user.assistant_profile.name
        return data


class LoginView(TokenObtainPairView):
    serializer_class = RoleAwareTokenObtainPairSerializer


# ---------- Public: Doctor self-registration ----------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_doctor(request):
    serializer = DoctorRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    doctor = serializer.save()

    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(doctor.user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'role': 'doctor',
        'doctor_id': doctor.id,
        'doctor_name': doctor.name,
        'display_name': doctor.name,
    }, status=status.HTTP_201_CREATED)


# ---------- Doctor-only: who am I + what can I do (drives frontend UI) ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    role = get_role(request.user)
    if role is None:
        return Response({'detail': 'No profile attached to this account.'}, status=403)
    doctor = get_doctor_for_user(request.user)
    display_name = doctor.name if role == 'doctor' else request.user.assistant_profile.name

    data = {
        'role': role,
        'username': request.user.username,
        'doctor_id': doctor.id,
        'doctor_name': doctor.name,
        'display_name': display_name,
        # Capability flags — frontend uses these to show/hide nav items and buttons.
        # Assistants: ONLY patient registration + medicine entry. Everything else is doctor-only.
        'can_manage_prescriptions': role == 'doctor',
        'can_manage_templates': role == 'doctor',
        'can_manage_assistants': role == 'doctor',
        'can_edit_doctor_profile': role == 'doctor',
    }
    return Response(MeSerializer(data).data)


# ---------- Doctor-only: create / list / deactivate assistants ----------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsDoctorOnly])
def assistants(request):
    doctor = request.user.doctor_profile

    if request.method == 'GET':
        qs = Assistant.objects.filter(doctor=doctor).order_by('-created_at')
        return Response(AssistantSerializer(qs, many=True).data)

    serializer = AssistantCreateSerializer(data=request.data, context={'doctor': doctor})
    serializer.is_valid(raise_exception=True)
    assistant = serializer.save()
    return Response(AssistantSerializer(assistant).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsDoctorOnly])
def assistant_detail(request, pk):
    doctor = request.user.doctor_profile
    try:
        assistant = Assistant.objects.get(pk=pk, doctor=doctor)
    except Assistant.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=404)

    if request.method == 'DELETE':
        # Deactivate rather than hard-delete, so historical data entries stay attributable.
        assistant.is_active = False
        assistant.user.is_active = False
        assistant.user.save()
        assistant.save()
        return Response(status=204)

    if 'is_active' in request.data:
        assistant.is_active = request.data['is_active']
        assistant.user.is_active = request.data['is_active']
        assistant.user.save()
    if 'name' in request.data:
        assistant.name = request.data['name']
    if 'phone' in request.data:
        assistant.phone = request.data['phone']
    assistant.save()
    return Response(AssistantSerializer(assistant).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctorOnly])
def reset_assistant_password(request, pk):
    doctor = request.user.doctor_profile
    try:
        assistant = Assistant.objects.get(pk=pk, doctor=doctor)
    except Assistant.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=404)
    new_password = request.data.get('password')
    if not new_password or len(new_password) < 6:
        return Response({'detail': 'Password must be at least 6 characters.'}, status=400)
    assistant.user.set_password(new_password)
    assistant.user.save()
    return Response({'detail': 'Password updated.'})
