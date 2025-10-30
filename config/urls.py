from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="Your API description",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("materials.urls")),
    path("api/users/", include("users.urls")),
    # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]  # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
