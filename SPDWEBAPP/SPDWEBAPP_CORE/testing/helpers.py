"""Request, clock and storage boundaries for real backend regression tests."""
from contextlib import contextmanager, ExitStack
from datetime import datetime, timezone as datetime_timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from django.test import Client, override_settings


def login_actor(client, user):
    """Establish identity for authorization tests; not evidence of password login."""
    client.force_login(user)
    return client


def csrf_client():
    """Return an enforcing client; caller must authenticate and obtain real tokens."""
    return Client(enforce_csrf_checks=True)


@contextmanager
def temporary_media():
    """Yield a fresh Path and restore settings before deleting its synthetic files."""
    with TemporaryDirectory(prefix="codex-spd-media-") as directory:
        with override_settings(MEDIA_ROOT=Path(directory)):
            yield Path(directory)


@contextmanager
def at_time(instant, *, targets=()):
    """Freeze Django's consumed clock and optional captured aliases; require aware time."""
    if isinstance(instant, str):
        instant = datetime.fromisoformat(instant.replace("Z", "+00:00"))
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("Regression clock must be timezone-aware")
    instant = instant.astimezone(datetime_timezone.utc)
    with ExitStack() as stack:
        for target in ("django.utils.timezone.now", *targets):
            stack.enter_context(patch(target, return_value=instant))
        yield instant
