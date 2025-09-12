from rest_framework import viewsets, permissions
from users.models import User
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Пока без авторизации

    def perform_update(self, serializer):
        instance = serializer.save()
        # Дополнительные действия при обновлении
        print(f"User {instance.email} updated")
