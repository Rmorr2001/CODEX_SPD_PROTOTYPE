"""Serve the real built frontend with synthetic Django/demo data for browser checks."""
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'SPDWEBAPP'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'SPDWEBAPP_CORE.testing.demo_settings'


def main():
    import django
    from django.conf import settings
    from django.core.management import call_command

    if not (settings.FRONTEND_DIST_DIR / 'index.html').is_file():
        raise SystemExit('Build frontend before starting the browser fixture server')
    with TemporaryDirectory(prefix='spd-browser-') as directory:
        settings.DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
                                         'NAME': str(Path(directory) / 'synthetic.sqlite3')}}
        settings.MEDIA_ROOT = Path(directory) / 'media'
        settings.STATIC_ROOT = Path(directory) / 'static'
        settings.MIDDLEWARE = [settings.MIDDLEWARE[0],
                              'whitenoise.middleware.WhiteNoiseMiddleware',
                              *settings.MIDDLEWARE[1:]]
        # Local HTTP browser fixtures only; deployed demo settings keep secure cookies.
        settings.SESSION_COOKIE_SECURE = False
        settings.CSRF_COOKIE_SECURE = False
        # Explicit trust for the optional loopback Vite dev server, never deployed settings.
        settings.CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:5173"]
        django.setup()
        call_command('migrate', interactive=False, verbosity=0)
        call_command('seed_railway_demo', verbosity=0)
        call_command('collectstatic', interactive=False, verbosity=0)
        port = os.environ.get('FRONTEND_TEST_PORT', '8765')
        call_command('runserver', f'127.0.0.1:{port}', use_reloader=False)


if __name__ == '__main__':
    main()
