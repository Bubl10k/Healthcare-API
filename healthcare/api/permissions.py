from rest_framework.permissions import BasePermission


class DoctorPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'doctor'
    

class PatientPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'patient'
    