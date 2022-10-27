from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class IsOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class HasSubscription(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        return user.is_staff or user.has_subscription
