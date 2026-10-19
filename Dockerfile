# syntax=docker/dockerfile:1
FROM node:24.19.0-bookworm-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
# Railway's Dockerfile parser supports cache mounts only; use its native CA trust.
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# Generate metadata from this build context; private/runtime output is excluded.
FROM python:3.12-slim AS file-tree
WORKDIR /source
COPY . .
ARG RAILWAY_GIT_COMMIT_SHA
RUN python tools/file_tree/build.py --root /source --output /tmp/file-tree.html --commit "$RAILWAY_GIT_COMMIT_SHA"

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=railway_demo.settings \
    FRONTEND_DIST_DIR=/app/frontend_dist
WORKDIR /app
COPY requirements.txt requirements-demo.txt ./
RUN pip install --no-cache-dir -r requirements-demo.txt && useradd --uid 1000 --create-home webapp
COPY --chown=webapp:webapp SPDWEBAPP/ ./
COPY --from=frontend /frontend/dist/ /app/frontend_dist/
COPY --from=file-tree /tmp/file-tree.html /app/railway_demo/static/railway_demo/file-tree.html
# Static collection uses synthetic build settings, without runtime secrets or a DB.
RUN DJANGO_SETTINGS_MODULE=SPDWEBAPP_CORE.build_settings python manage.py collectstatic --noinput
USER webapp
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_railway_demo && exec gunicorn SPDWEBAPP_CORE.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 60 --access-logfile -"]
