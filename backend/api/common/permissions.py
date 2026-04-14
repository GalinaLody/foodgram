from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Права доступа для автора.

    Анонимному пользователю предоставляется право на чтение.
    Авторизованному пользователю разрешено создавать объект.
    Изменять, удалять объект может только его автор.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
