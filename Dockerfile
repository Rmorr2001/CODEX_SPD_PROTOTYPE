FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=railway_demo.settings
WORKDIR /app
COPY requirements.txt requirements-demo.txt ./
RUN pip install --no-cache-dir -r requirements-demo.txt
COPY SPDWEBAPP/ ./
RUN python manage.py collectstatic --noinput && useradd --create-home webapp
USER webapp
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_railway_demo && exec gunicorn SPDWEBAPP_CORE.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 60 --access-logfile -"]
