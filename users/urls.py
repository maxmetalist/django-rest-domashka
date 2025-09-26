from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import UserViewSet, UserProfileView, PaymentViewSet, UserRegistrationView, UserLoginView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
