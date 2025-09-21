from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from users.filters import PaymentFilter
from users.models import User, Payment
from users.permissions import IsProfileOwner
from users.serializers import (
    UserSerializer,
    PaymentSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer, UserPrivateSerializer, UserPublicSerializer
)


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Создаем JWT токены
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })

        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Разрешаем регистрацию (create) без авторизации
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsProfileOwner()]
        else:
            return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от контекста"""
        if self.action in ['retrieve', 'update', 'partial_update']:
            # Для своего профиля используем приватный сериализатор
            if self.get_object() == self.request.user:
                return UserPrivateSerializer
            # Для чужого профиля - публичный
            return UserPublicSerializer
        return UserPublicSerializer

    def get_object(self):
        """Переопределяем для возможности просмотра любого профиля"""
        if self.kwargs.get('pk') == 'me':
            return self.request.user

        obj = get_object_or_404(User, pk=self.kwargs.get('pk'))

        # Для действий, требующих владения, проверяем права
        if self.action in ['update', 'partial_update', 'destroy']:
            self.check_object_permissions(self.request, obj)

        return obj

    def retrieve(self, request, *args, **kwargs):
        """Просмотр профиля - свой или чужой"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Для админов показываем все платежи
        if self.request.user.is_staff:
            return Payment.objects.all()
        # Для обычных юзеров только их платежи
        return Payment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Автоматически назначаем текущего юзера
        serializer.save(user=self.request.user)


class UserProfileView(generics.RetrieveAPIView):
    """Профиль текущего юзера по умолчанию свой"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
