from rest_framework import permissions

class IsClinicianOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['clinician', 'admin']

class IsOwnerOrClinician(permissions.BasePermission):
    """
    Allows access if:
    - user is patient and object belongs to them, OR
    - user is clinician/admin (handled in view's queryset for safety)
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if user.role == 'clinician':
            # For BPReading or Alert, check patient's clinician
            patient = getattr(obj, 'patient', obj)
            return hasattr(patient, 'clinician') and patient.clinician == user
        # patient role
        patient = getattr(obj, 'patient', obj)
        return hasattr(patient, 'user') and patient.user == user