from django.urls import path, include
from rest_framework.routers import DefaultRouter
from materials.views import (
    CourseViewSet,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonCreateAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    SubscriptionAPIView,
    SubscriptionDetailAPIView,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet)

urlpatterns = [
    # Уроки
    path("", include(router.urls)),
    path("lessons/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lessons/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-detail"),
    path("lessons/<int:pk>/update/", LessonUpdateAPIView.as_view(), name="lesson-update"),
    path("lessons/<int:pk>/delete/", LessonDestroyAPIView.as_view(), name="lesson-delete"),
    # Подписки
    path("subscriptions/", SubscriptionAPIView.as_view(), name="subscriptions"),
    path("subscriptions/<int:pk>/", SubscriptionDetailAPIView.as_view(), name="subscription-detail"),
] + router.urls
