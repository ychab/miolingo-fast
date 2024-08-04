from typing import Any

from httpx import ASGITransport, AsyncClient, Headers

from miolingo.main import app
from miolingo.models import AccessToken


class AsyncClientTest(AsyncClient):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("base_url", "http://test")
        kwargs.setdefault("transport", ASGITransport(app=app))
        super().__init__(*args, **kwargs)

    def url_path_for(self, name: str) -> str:
        return self._transport.app.url_path_for(name)

    def force_login(self, access_token: AccessToken) -> None:
        # @TODO - should be binary ?? should it be base64 encoded too?
        self.headers.update(
            {
                "Authorization": f"Bearer {access_token.token}",
            }
        )

    def force_logout(self) -> None:
        self.headers = Headers()
