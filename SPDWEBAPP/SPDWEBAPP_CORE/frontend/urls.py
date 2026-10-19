from django.urls import re_path
from .views import shell

urlpatterns = [re_path(r'^(?P<path>.*)$', shell, name='frontend_shell')]
