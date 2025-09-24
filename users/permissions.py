from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает полный доступ владельцу,
    другим юзерам дырку от бублика (только чтение)
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsProfileOwner(permissions.BasePermission):
    """Проверяет, является ли юзер владельцем профиля"""

    def has_object_permission(self, request, view, obj):
        return obj == request.user
