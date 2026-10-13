"""Our Railway demo configuration; this file stores no literal secret values."""  # New: document the demo-owned configuration.
import os  # New: obtain deployed configuration from runtime bindings.
import secrets  # New: generate an ephemeral key when no stable key is configured.

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or secrets.token_urlsafe(50)  # New: keep the key out of source and logs; fallback sessions expire on restart.
ADMIN_URL = "admin"  # New: satisfy the app's existing admin URL contract; public demo admin access is blocked.
ENVIRONMENT = "production"  # New: keep Django debug output off on the public Railway deployment.
DEMO_DATABASE_PATH = os.environ.get("DEMO_DATABASE_PATH", "/tmp/spd-mizzou-demo.sqlite3")  # New: isolate fictional data from the original database.
DEMO_MEDIA_ROOT = os.environ.get("DEMO_MEDIA_ROOT", "/tmp/spd-mizzou-media")  # New: keep demo uploads disposable and separate from production media.
