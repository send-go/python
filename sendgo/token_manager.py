from __future__ import annotations

import base64
import threading
import time
from typing import TYPE_CHECKING

import requests

from .exceptions import SendgoError

if TYPE_CHECKING:
    pass

_NO_REFRESH_CODES = frozenset({
    "INVALID_AUTH_HEADER", "INVALID_BASIC_AUTH", "INVALID_BASIC_AUTH_PAYLOAD",
    "INVALID_ACCESS_KEY", "INVALID_SECRET_KEY", "ACCESS_KEY_NOT_APPROVED",
    "TEAM_REQUIRED_FOR_KAKAO", "IP_NOT_ALLOWED", "INVALID_SENDER_KEY", "INVALID_KAKAO_SENDER_KEY",
})

_TOKEN_TTL = 50 * 60  # 50분


class TokenManager:
    """토큰 발급 및 50분 캐시 관리."""

    def __init__(self, base_url: str, access_key: str, secret_key: str, api_version: str) -> None:
        self._base_url = base_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._api_version = api_version
        self._token: str | None = None
        self._expires_at: float = 0.0
        self._lock = threading.Lock()

    def get_token(self) -> str:
        with self._lock:
            if self._token and time.monotonic() < self._expires_at:
                return self._token
            return self._fetch_token()

    def invalidate(self) -> None:
        with self._lock:
            self._token = None
            self._expires_at = 0.0

    def should_refresh(self, status: int, error_code: str | None) -> bool:
        if status not in (401, 403):
            return False
        if self._api_version == "v2" and error_code in _NO_REFRESH_CODES:
            return False
        return True

    def _fetch_token(self) -> str:
        url = f"{self._base_url}/api/{self._api_version}/token"
        credentials = base64.b64encode(f"{self._access_key}:{self._secret_key}".encode()).decode()

        resp = requests.post(url, headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {credentials}",
        }, timeout=10)

        body = resp.json() if resp.content else {}

        if not resp.ok or not body.get("data", {}).get("token"):
            raise SendgoError.from_response(resp.status_code, body, "token", self._api_version)

        self._token = body["data"]["token"]
        self._expires_at = time.monotonic() + _TOKEN_TTL
        return self._token
