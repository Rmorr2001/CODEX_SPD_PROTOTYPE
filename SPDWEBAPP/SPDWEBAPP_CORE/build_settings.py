"""Static-only image assembly; never import runtime configuration or credentials."""
from pathlib import Path
from .web_settings import FRONTEND_STATIC_DIRS

BASE_DIR = Path(__file__).resolve().parents[1]
SECRET_KEY = 'static-assembly-only-not-a-runtime-key'
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'adminsortable2', 'AUTHENTICATE', 'PARLEYPRO', 'PHILANTHROPY', 'NEWMEMBER',
    'HOME', 'MISC', 'railway_demo',
]
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static', *FRONTEND_STATIC_DIRS]
USE_TZ = True
