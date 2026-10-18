"""Synthetic demo mode, without importing secret_config or deployment settings."""
from copy import deepcopy
from .settings import *  # noqa: F403

DEMO_MODE = True
ROOT_URLCONF = "railway_demo.urls"
MIDDLEWARE = [*MIDDLEWARE, "railway_demo.middleware.DemoBoundaryMiddleware"]  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
TEMPLATES = deepcopy(TEMPLATES)  # noqa: F405
TEMPLATES[0]["OPTIONS"]["context_processors"].append("railway_demo.context.demo_state")
