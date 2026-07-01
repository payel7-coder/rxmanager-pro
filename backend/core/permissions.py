"""
Role-based access control.

Two roles exist:
  - Doctor account    -> full access to everything (their own data only)
  - Assistant account -> can ONLY create/edit Patients and Medicines (data entry)
                          cannot touch Prescriptions, Templates, Doctor profile, or other Assistants

Every doctor and assistant only ever sees data belonging to their own clinic
(doctor.patients, doctor.prescriptions, etc.) — never another doctor's data.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Doctor, Assistant


def get_doctor_for_user(user):
    """Return the Doctor row that owns this user's clinic, whether the
    logged-in user IS the doctor, or is an assistant working for one."""
    if hasattr(user, 'doctor_profile'):
        return user.doctor_profile
    if hasattr(user, 'assistant_profile'):
        return user.assistant_profile.doctor
    return None


def get_role(user):
    if hasattr(user, 'doctor_profile'):
        return 'doctor'
    if hasattr(user, 'assistant_profile'):
        return 'assistant'
    return None


class IsDoctorOrAssistant(BasePermission):
    """Base: must be authenticated AND linked to a Doctor or Assistant profile."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return get_doctor_for_user(request.user) is not None


class IsDoctorOnly(BasePermission):
    """Full-access endpoints: Prescriptions, Templates, Doctor profile, Assistant management.
    Assistants are blocked entirely (even read-only) per the requirement
    'assistant only can perform data entry like new patient registration, add medicine'."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return get_role(request.user) == 'doctor'


class IsDoctorOrAssistantDataEntry(BasePermission):
    """Patients + Medicines endpoints: both roles allowed (assistants do data entry here)."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return get_role(request.user) in ('doctor', 'assistant')
