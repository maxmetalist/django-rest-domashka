from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOrModerator(permissions.BasePermission):
    """Разрешает доступ владельцу объекта или модератору.
    У владельца полный доступ.
    Модератор может только читать (не редактировать)
    У остальных вообще нет доступа"""

    def has_object_permission(self, request, view, obj):
        # Владелец имеет полный доступ
        if obj.owner == request.user:
            return True

        # Модератор может только читать (без редактирования)
        if request.user.groups.filter(name="moderators").exists():
            return request.method in permissions.SAFE_METHODS

        # Остальные не имеют доступа
        return False


class IsNotModerator(permissions.BasePermission):
    """Запрещает доступ модераторам для создания/удаления"""

    def has_permission(self, request, view):
        if request.method in ["POST", "DELETE"]:
            return not request.user.groups.filter(name="moderators").exists()
        return True
