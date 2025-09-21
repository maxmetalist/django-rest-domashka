from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, UserProfileView, PaymentViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]