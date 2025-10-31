from django.urls import include, path
from rest_framework.routers import DefaultRouter

from materials.views import (
    CourseViewSet,
    LessonViewSet,
    PaymentViewSet,
    SubscriptionAPIView,
    SubscriptionDetailAPIView,
    payment_status,
    stripe_webhook,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"lessons", LessonViewSet, "lesson")
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    # Уроки
    path("", include(router.urls)),
    path("subscriptions/", SubscriptionAPIView.as_view(), name="subscriptions"),
    path("subscriptions/<int:pk>/", SubscriptionDetailAPIView.as_view(), name="subscription-detail"),
    path("payments/<int:payment_id>/status/", payment_status, name="payment-status"),
    path("webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
] + router.urls
