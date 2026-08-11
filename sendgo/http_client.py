from __future__ import annotations

import base64

import requests

from .exceptions import SendgoError
from .token_manager import TokenManager


class HttpClient:
    def __init__(self, token_manager: TokenManager, base_url: str, api_version: str) -> None:
        self._token_manager = token_manager
        self._base_url = base_url
        self._api_version = api_version
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    def post(self, path: str, body: dict) -> dict:
        return self._request("POST", path, body=body, is_retry=False)

    def get(self, path: str, params: dict | None = None) -> dict:
        """GET request, used by the campaign lookup endpoints."""
        return self._request("GET", path, params=params, is_retry=False)

    def delete(self, path: str) -> dict:
        """`_request()` drives the verb, so DELETE only needs to skip the body."""
        return self._request("DELETE", path, is_retry=False)

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict | None = None,
        params: dict | None = None,
        is_retry: bool,
    ) -> dict:
        url = f"{self._base_url}/api/{self._api_version}/{path}"
        token = self._token_manager.get_token()

        resp = self._session.request(
            method,
            url,
            json=body,
            # Drop unset filters so the server applies its own defaults.
            params={k: v for k, v in (params or {}).items() if v is not None} or None,
            headers={"Authorization": self._make_bearer(token)},
            timeout=15,
        )

        response_body = resp.json() if resp.content else {}

        if not resp.ok:
            error_code = response_body.get("code")
            endpoint = path.split("/")[-1]
            if not is_retry and self._token_manager.should_refresh(resp.status_code, error_code):
                self._token_manager.invalidate()
                return self._request(method, path, body=body, params=params, is_retry=True)
            raise SendgoError.from_response(resp.status_code, response_body, endpoint, self._api_version)

        return response_body

    def _make_bearer(self, token: str) -> str:
        if self._api_version == "v2":
            return f"Bearer {token}"
        return "Bearer " + base64.b64encode(token.encode()).decode()
