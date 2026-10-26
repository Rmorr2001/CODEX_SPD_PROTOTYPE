"""Shared API and bundled-frontend settings; no runtime credentials are loaded."""
import os
from pathlib import Path
from SPDWEBAPP_CORE.frontend.assets import immutable_file_test

WEB_APPS = ['rest_framework', 'drf_spectacular']
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'SPDWEBAPP_CORE.api.errors.domain_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'CODEX SPD API', 'VERSION': '1.0.0', 'SERVE_INCLUDE_SCHEMA': False,
    # Liveness and request approval share a field name, but have distinct contracts.
    'ENUM_NAME_OVERRIDES': {
        'LivenessStatusEnum': ['ok'],
        'ApprovalStatusEnum': ['approved', 'requested', 'denied'],
    },
}
# Local builds use frontend/dist; Docker supplies its fixed, image-owned directory.
FRONTEND_DIST_DIR = Path(os.environ.get(
    'FRONTEND_DIST_DIR', Path(__file__).resolve().parents[2] / 'frontend/dist'))
FRONTEND_STATIC_DIRS = [('app/assets', FRONTEND_DIST_DIR / 'assets')] if (
    FRONTEND_DIST_DIR / 'assets').is_dir() else []
WHITENOISE_IMMUTABLE_FILE_TEST = immutable_file_test
