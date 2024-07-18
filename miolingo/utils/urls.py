from urllib.parse import urlencode, urlparse, urlunsplit

from miolingo import settings


def build_frontend_url(path: str, query: dict | None = None, fragment: str | None = None) -> str:
    scheme, netloc = urlparse(settings.FRONTEND_URL_BASE)[:2]
    query_str = urlencode(query) if query else None
    return str(urlunsplit((scheme, netloc, path, query_str, fragment)))
