"""Serve only the fixed build entry point; React owns routing beneath /app/."""
from pathlib import Path
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_safe


@require_safe
@cache_control(no_cache=True)
def shell(request, path=''):
    """Return built HTML or a controlled 503; URL text never selects a file."""
    try:
        entry = (Path(settings.FRONTEND_DIST_DIR) / 'index.html').open('rb')
    except (FileNotFoundError, NotADirectoryError):
        return HttpResponse('Application temporarily unavailable.', status=503,
                            content_type='text/plain')
    return FileResponse(entry, content_type='text/html; charset=utf-8')
