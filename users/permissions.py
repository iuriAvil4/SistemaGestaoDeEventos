from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.profile_type == 'ADMIN'
    
    
class IsOrganizerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.profile_type == 'ORGANIZER'
    

class IsParticipantUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.profile_type == 'PARTICIPANT'