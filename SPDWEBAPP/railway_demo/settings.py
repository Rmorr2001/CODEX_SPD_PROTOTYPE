"""Isolated Railway demo settings; never load a developer's secret_config file."""
import importlib.util
import os
import sys
from pathlib import Path

# Load only our clone's config; never discover a machine-local account/config file.
config_path = Path(__file__).resolve().parents[1] / "secret_config.py"
config_spec = importlib.util.spec_from_file_location("secret_config", config_path)
config = importlib.util.module_from_spec(config_spec)
sys.modules["secret_config"] = config
config_spec.loader.exec_module(config)

from SPDWEBAPP_CORE.settings import *  # noqa: E402,F403

DEMO_MODE = True
DEBUG = False
ROOT_URLCONF = "railway_demo.urls"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver", "healthcheck.railway.app"]
public_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
DEMO_PUBLIC_DOMAIN = public_domain
if public_domain:
    ALLOWED_HOSTS.append(public_domain)
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": config.DEMO_DATABASE_PATH}}
MEDIA_ROOT = Path(config.DEMO_MEDIA_ROOT)
STATIC_ROOT = BASE_DIR / "staticfiles"
INSTALLED_APPS = [*INSTALLED_APPS, "railway_demo"]
MIDDLEWARE = [*MIDDLEWARE]
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
MIDDLEWARE.append("railway_demo.middleware.DemoBoundaryMiddleware")
TEMPLATES[0]["OPTIONS"]["context_processors"].append("railway_demo.context.demo_state")
LOGIN_URL = "/auth/login/"
# Railway terminates HTTPS; do not redirect the internal HTTP health probe.
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# The explorer changes with each build; revalidate its static URL on reload.
from railway_demo.static_headers import add_headers as WHITENOISE_ADD_HEADERS_FUNCTION
