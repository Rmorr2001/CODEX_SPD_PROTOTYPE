"""Shared presentation-link safety boundary for public and authenticated read models."""
from urllib.parse import urlsplit


def safe_public_url(value):
    """Reject executable, protocol-relative and malformed configured links."""
    if not value or any(char.isspace() for char in value) or '\\' in value:
        return None
    try:
        parsed = urlsplit(value)
        parsed.port  # Reject malformed ports rather than returning an unusable URL.
    except ValueError:
        return None
    if parsed.username or parsed.password:
        return None
    if value.startswith('/') and not value.startswith('//'):
        return value
    return value if parsed.scheme in {'http', 'https'} and parsed.hostname else None

