from django.urls import path, include
from rest_framework.routers import DefaultRouter
from materials.views import CourseViewSet, LessonViewSet, SubscriptionAPIView, SubscriptionDetailAPIView

router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"lessons", LessonViewSet, "lesson")

urlpatterns = [
    # Уроки
    path("", include(router.urls)),
    path("subscriptions/", SubscriptionAPIView.as_view(), name="subscriptions"),
    path("subscriptions/<int:pk>/", SubscriptionDetailAPIView.as_view(), name="subscription-detail"),
] + router.urls
