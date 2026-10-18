"""Standalone synthetic settings: no runtime config, environment or member DB."""
import atexit
import shutil
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
TEST_ROOT = Path(tempfile.mkdtemp(prefix="codex-spd-tests-"))
atexit.register(shutil.rmtree, TEST_ROOT, ignore_errors=True)
SECRET_KEY = "synthetic-regression-key-not-for-deployment"
DEBUG = False
ADMIN_URL = "admin"
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1", "healthcheck.railway.app"]
ROOT_URLCONF = "SPDWEBAPP_CORE.urls"
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "adminsortable2", "AUTHENTICATE", "PARLEYPRO", "MISC", "PHILANTHROPY",
    "NEWMEMBER", "HOME", "railway_demo",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug", "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages",
    ]},
}]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Chicago"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = ""
STATIC_URL = "/static/"
STATIC_ROOT = TEST_ROOT / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = TEST_ROOT / "media"
MEDIA_ROOT.mkdir()
DEMO_MODE = False
DEMO_PUBLIC_DOMAIN = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
