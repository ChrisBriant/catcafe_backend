from rest_framework import permissions
#from quiz.models import Question


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        print("Owner",obj.owner)
        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user

def is_authorised(user,obj):
    return user.is_superuser or user == obj.user
