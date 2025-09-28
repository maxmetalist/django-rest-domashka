import stripe
from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response

from materials.models import Course, Lesson, Subscription
from materials.paginators import CoursePagination, LessonPagination, SubscriptionPagination
from materials.serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer, PaymentSerializer, \
    CreatePaymentSerializer
from materials.permissions import IsOwnerOrModerator, IsNotModerator, IsOwner
from materials.services.stripe_service import StripeService
from users.models import Payment


class CourseViewSet(viewsets.ModelViewSet):
    """Контроллер курсов через ViewSet"""

    queryset = Course.objects.annotate(lessons_count=Count("lessons"))
    serializer_class = CourseSerializer
    pagination_class = CoursePagination

    def get_permissions(self):
        """Динамическое назначение прав в зависимости от действия"""
        if self.action == "create":
            # Создавать могут только не-модераторы
            return [permissions.IsAuthenticated(), IsNotModerator()]
        elif self.action == "destroy":
            # Удалять могут только не-модераторы и только свои курсы
            return [permissions.IsAuthenticated(), IsNotModerator(), IsOwner()]
        elif self.action in ["update", "partial_update"]:
            # Редактировать могут владельцы или модераторы
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        else:
            # Просматривать могут все аутентифицированные (аноним в обломе)
            return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """Автоматически назначаем владельца при создании"""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Фильтрация queryset в зависимости от прав"""
        user = self.request.user

        # Модераторы видят все курсы (но только для чтения)
        if user.groups.filter(name="moderators").exists():
            return Course.objects.annotate(lessons_count=Count("lessons"))

        # Анонимные юзеры не видят ничего
        if not user.is_authenticated:
            return Course.objects.none()

        # Обычные юзеры видят только свои курсы
        return Course.objects.filter(owner=user).annotate(lessons_count=Count("lessons"))

    def get_serializer_context(self):
        """Добавляем request в контекст сериализатора"""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def create_payment_session(self, request, pk=None):
        """Создание сессии оплаты для курса"""
        course = self.get_object()

        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            # Если у курса нет Stripe product/price, создаем их
            if not course.stripe_product_id or not course.stripe_price_id:
                product = StripeService.create_product(
                    name=course.title,
                    description=course.description or f"Курс {course.title}"
                )

                price = StripeService.create_price(
                    product_id=product.id,
                    amount=course.price
                )

                course.stripe_product_id = product.id
                course.stripe_price_id = price.id
                course.save()

            success_url = serializer.validated_data['success_url']
            cancel_url = serializer.validated_data['cancel_url']

            session = StripeService.create_checkout_session(
                price_id=course.stripe_price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'course_id': str(course.id),
                    'user_id': str(request.user.id)
                }
            )

            # Создаем запись о платеже
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                stripe_session_id=session.id,
                amount=course.price
            )

            return Response({
                'session_id': session.id,
                'url': session.url,
                'payment_id': payment.id
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    pagination_class = LessonPagination

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsNotModerator()]
        elif self.action == "destroy":
            return [permissions.IsAuthenticated(), IsNotModerator(), IsOwner()]
        elif self.action in ["update", "partial_update"]:
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        else:
            return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        if not user.is_authenticated:
            return Lesson.objects.none()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SubscriptionAPIView(generics.ListAPIView, generics.CreateAPIView):
    """Контроллер для управления подписками"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionSerializer
    pagination_class = SubscriptionPagination

    def get_queryset(self):
        """Возвращает подписки текущего юзера"""
        return Subscription.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        """Создание или удаление подписки"""
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response({"error": "course_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, id=course_id)

        # Проверяем, существует ли уже подписка
        subscription, created = Subscription.objects.get_or_create(user=user, course=course)

        if created:
            # Подписка создана
            serializer = SubscriptionSerializer(subscription)
            return Response(
                {"message": f'У тя подписка на курс "{course.title}"', "subscription": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            # Подписка уже существует - удаляем ее (отписка)
            subscription.delete()
            return Response(
                {
                    "message": f'И правильно, отпишись от курса,'
                               f'не забивай свой не окрепший детский мозг "{course.title}"'
                },
                status=status.HTTP_200_OK,
            )

    def get(self, request, *args, **kwargs):
        """Получение списка подписок пользователя"""
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


class SubscriptionDetailAPIView(generics.DestroyAPIView):
    """Контроллер для управления конкретной подпиской"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        """Каждый юзер может удалять только свои подписки"""
        return Subscription.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Удаление подписки по ID"""
        subscription = self.get_object()
        course_title = subscription.course.title
        subscription.delete()
        return Response({"message": f'Вы отписались от курса "{course_title}"'}, status=status.HTTP_200_OK)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Просмотр истории платежей"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer
    pagination_class = LessonPagination  # Можно использовать существующий пагинатор

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def payment_status(request, payment_id):
    """Проверка статуса платежа"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)

    # Обновляем статус из Stripe
    session = StripeService.get_session(payment.stripe_session_id)

    if session.payment_status == 'paid' and payment.status != 'completed':
        payment.status = 'completed'
        payment.save()

    serializer = PaymentSerializer(payment)
    return Response(serializer.data)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        try:
            payment = Payment.objects.get(stripe_session_id=session.id)
            payment.status = 'completed'
            payment.save()

            # Автоматически создаем подписку при успешной оплате
            Subscription.objects.get_or_create(
                user=payment.user,
                course=payment.course
            )

        except Payment.DoesNotExist:
            pass

    return HttpResponse(status=200)
