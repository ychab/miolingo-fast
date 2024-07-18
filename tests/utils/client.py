from typing import Any, Optional

from httpx import ASGITransport, AsyncClient, Headers

from miolingo import settings
from miolingo.main import app


class AsyncClientTest(AsyncClient):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("base_url", "http://test")
        kwargs.setdefault("transport", ASGITransport(app=app))
        super().__init__(*args, **kwargs)

    def url_path_for(self, name: str) -> str:
        return self._transport.app.url_path_for(name)

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        username = username or settings.API_HTTP_AUTH_USER
        password = password or settings.API_HTTP_AUTH_PASS
        token = None

        # @TODO - should be binary ?? should it be base64 encoded too?
        self.headers.update(
            {
                "Authorization": f"Bearer {token}",
            }
        )

    def logout(self) -> None:
        self.headers = Headers()
