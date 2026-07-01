from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Doctor, Assistant


class DoctorRegisterSerializer(serializers.Serializer):
    """Public sign-up: creates the User + Doctor profile together."""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    name = serializers.CharField(max_length=200)
    qualification = serializers.CharField(max_length=300)
    specialization = serializers.CharField(max_length=200)
    registration_no = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField(required=False, allow_blank=True)
    clinic_name = serializers.CharField(max_length=200)
    clinic_address = serializers.CharField()
    clinic_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_registration_no(self, value):
        if Doctor.objects.filter(registration_no=value).exists():
            raise serializers.ValidationError("A doctor with this registration number already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
        )
        doctor = Doctor.objects.create(
            user=user,
            name=validated_data['name'],
            qualification=validated_data['qualification'],
            specialization=validated_data['specialization'],
            registration_no=validated_data['registration_no'],
            phone=validated_data['phone'],
            email=validated_data.get('email', ''),
            clinic_name=validated_data['clinic_name'],
            clinic_address=validated_data['clinic_address'],
            clinic_phone=validated_data.get('clinic_phone', ''),
        )
        return doctor


class AssistantCreateSerializer(serializers.Serializer):
    """Used by a logged-in Doctor to create an Assistant account under their clinic."""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        doctor = self.context['doctor']
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        assistant = Assistant.objects.create(
            user=user,
            doctor=doctor,
            name=validated_data['name'],
            phone=validated_data.get('phone', ''),
        )
        return assistant


class AssistantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Assistant
        fields = ['id', 'username', 'name', 'phone', 'is_active', 'created_at']


class MeSerializer(serializers.Serializer):
    """Returned on login / on app load — tells the frontend who is logged in and what they can do."""
    role = serializers.CharField()
    username = serializers.CharField()
    doctor_id = serializers.IntegerField()
    doctor_name = serializers.CharField()
    display_name = serializers.CharField()
    can_manage_prescriptions = serializers.BooleanField()
    can_manage_templates = serializers.BooleanField()
    can_manage_assistants = serializers.BooleanField()
    can_edit_doctor_profile = serializers.BooleanField()
