from django.urls import path, re_path
from drf_spectacular.renderers import OpenApiJsonRenderer
from drf_spectacular.views import SpectacularAPIView
from rest_framework.permissions import AllowAny
from .views import ApiNotFoundView, StatusView
from HOME.api import PublicHomeView
from HOME.api_about import PublicAboutView

urlpatterns = [
    path('v1/public/about/', PublicAboutView.as_view(), name='api_public_about'),
    path('v1/public/home/', PublicHomeView.as_view(), name='api_public_home'),
    path('v1/status/', StatusView.as_view(), name='api_status'),
    path('v1/schema/', SpectacularAPIView.as_view(
        authentication_classes=[], permission_classes=[AllowAny],
        renderer_classes=[OpenApiJsonRenderer]), name='api_schema'),
    re_path(r'^.*$', ApiNotFoundView.as_view(), name='api_not_found'),
]
