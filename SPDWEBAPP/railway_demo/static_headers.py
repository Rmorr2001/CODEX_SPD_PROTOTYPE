"""Cache policy for build-generated demo resources."""


def add_headers(headers, path, url):
    """Revalidate the explorer on reload so a deployment cannot stay cached."""
    if url.endswith("/railway_demo/file-tree.html"):
        headers["Cache-Control"] = "no-cache"
