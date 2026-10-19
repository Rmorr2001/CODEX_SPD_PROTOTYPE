"""Cache only Vite's content-hashed assets indefinitely; HTML always revalidates."""
import re


def immutable_file_test(path, url):
    """Recognize Vite filenames without treating unhashed files as immutable."""
    return bool(re.fullmatch(r'/static/app/assets/[^/]+-[A-Za-z0-9_-]{8,}\.[a-z0-9]+', url))
