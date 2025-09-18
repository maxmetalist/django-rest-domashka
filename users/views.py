from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, generics
from rest_framework.filters import OrderingFilter

from users.filters import PaymentFilter
from users.models import User, Payment
from users.serializers import UserSerializer, PaymentSerializer, UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Пока без авторизации

    def perform_update(self, serializer):
        instance = serializer.save()
        # Дополнительные действия при обновлении
        print(f"User {instance.email} updated")


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']  # По умолчанию сортировка по убыванию даты

    def get_queryset(self):
        # Для администраторов показываем все платежи
        if self.request.user.is_staff:
            return Payment.objects.all()
        # Для обычных пользователей только их платежи
        return Payment.objects.filter(user=self.request.user)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
