from rest_framework import permissions


class IsClinicianOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['clinician', 'admin']

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        print(f"User: {request.user} | Role: {request.user.role} | Is auth: {request.user.is_authenticated}")
        return request.user.is_authenticated and request.user.role == 'patient'



class IsOwnerOrClinician(permissions.BasePermission):
    """
    Custom permission:
    - Admin: Full access (read/write) to everything.
    - Clinician: Read/Write access only to their assigned patients.
    - Patient: Read/Write access to their own data only.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # Admin and clinician can do anything (within their scope)
        if user.role in ['admin', 'clinician']:
            return True

        # Patient: allow GET (list) and POST (create) if it's their own data
        if user.role == 'patient':
            # restrict access to owned resources.
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Helper to get the patient object (works for Patient, BPReading, Alert, etc.)
        if hasattr(obj, 'patient'):
            patient = obj.patient
        else:
            patient = obj  # Assume obj is a Patient instance

        # SAFE METHODS (GET, HEAD, OPTIONS) – read-only
        if request.method in permissions.SAFE_METHODS:
            if user.role == 'admin':
                return True
            if user.role == 'clinician':
                return hasattr(patient, 'clinician') and patient.clinician == user
            if user.role == 'patient':
                return hasattr(patient, 'user') and patient.user == user
            return False


        # WRITE METHODS (POST, PUT, PATCH, DELETE)
        if user.role == 'admin':
            return True
        if user.role == 'clinician':
            return hasattr(patient, 'clinician') and patient.clinician == user
        if user.role == 'patient':
            # Patient can write only if they own the object
            return hasattr(patient, 'user') and patient.user == user
        return False
