from django.urls import include, path
from . import views

urlpatterns = [path("demo/enter/", views.enter, name="demo_enter"), path("", include("SPDWEBAPP_CORE.urls"))]
