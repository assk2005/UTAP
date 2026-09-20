from rest_framework.permissions import BasePermission

class IsRecruiter(BasePermission):
    def has_permission(self,request,view):
        return request.user.role=='recruiter'

class IsCandidate(BasePermission):
    def has_permission(self,request,view):
        return request.user.role=='candidate'

class IsAdmin(BasePermission):
    def has_permission(self,request,view):
        return request.user.role=='admin'
