from rest_framework import permissions

class IsClinicianOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['clinician', 'admin']

class IsOwnerOrClinician(permissions.BasePermission):
    """
    Custom permission:
    - Admin: Full access (read/write) to everything.
    - Clinician: Read/Write access only to their assigned patients.
    - Patient: READ-ONLY access to their own data. No writes allowed.
    """

    def has_permission(self, request, view):
        # All authenticated users can list/retrieve, but writes are checked later.
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Helper to get the patient object (works for Patient, BPReading, Alert)
        if hasattr(obj, 'patient'):
            patient = obj.patient
        else:
            patient = obj  # Assume obj is a Patient instance

        # SAFE METHODS (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            if user.role == 'admin':
                return True
            if user.role == 'clinician':
                return hasattr(patient, 'clinician') and patient.clinician == user
            if user.role == 'patient':
                return hasattr(patient, 'user') and patient.user == user
            return False

        # WRITE METHODS (POST, PUT, PATCH, DELETE)
        # Patients are strictly forbidden from writing
        if user.role == 'patient':
            return False

        # Admins can write anything
        if user.role == 'admin':
            return True

        # Clinicians can only write to their assigned patients
        if user.role == 'clinician':
            return hasattr(patient, 'clinician') and patient.clinician == user

        return False
    