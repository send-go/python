from __future__ import annotations

import base64
import json
from typing import Any

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

    def put(self, path: str, body: dict) -> dict:
        return self._request("PUT", path, body=body, is_retry=False)

    def patch(self, path: str, body: dict) -> dict:
        return self._request("PATCH", path, body=body, is_retry=False)

    def delete(self, path: str) -> dict:
        """`_request()` drives the verb, so DELETE only needs to skip the body."""
        return self._request("DELETE", path, is_retry=False)

    def post_multipart(
        self,
        path: str,
        fields: dict | None = None,
        files: dict | None = None,
    ) -> dict:
        """multipart/form-data POST — 서류·이미지 첨부가 있는 관리 API 전용.

        발신번호 등록과 이미지 템플릿은 JSON 으로 보낼 수 없다. multipart 에는
        배열도 불리언도 없으므로, 리스트/딕트는 JSON 문자열로 눌러 보낸다 —
        서버가 그렇게 받아 읽는다.

        ``files`` 값은 ``requests`` 가 받는 형태를 그대로 쓴다: 열린 파일
        객체, ``(filename, fileobj)``, ``(filename, fileobj, content_type)``.
        같은 필드에 여러 파일을 붙이려면 리스트로 넘긴다 — 서버가
        ``attachments[0]`` 형태를 기대하므로 인덱스를 붙여 보낸다.
        """
        return self._multipart_request(path, fields or {}, files or {}, is_retry=False)

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

    def _multipart_request(
        self,
        path: str,
        fields: dict,
        files: dict,
        *,
        is_retry: bool,
    ) -> dict:
        url = f"{self._base_url}/api/{self._api_version}/{path}"
        token = self._token_manager.get_token()

        data: dict[str, str] = {}
        for key, value in fields.items():
            if value is None:
                continue
            if isinstance(value, bool):
                data[key] = "1" if value else "0"
            elif isinstance(value, (list, dict)):
                data[key] = json.dumps(value, ensure_ascii=False)
            else:
                data[key] = str(value)

        payload_files: list[tuple[str, Any]] = []
        for key, value in files.items():
            if value is None:
                continue
            if isinstance(value, list):
                for index, entry in enumerate(value):
                    payload_files.append((f"{key}[{index}]", entry))
            else:
                payload_files.append((key, value))

        # 세션 기본 헤더의 Content-Type: application/json 을 반드시 비워야 한다.
        # 남겨 두면 requests 가 붙이는 multipart boundary 를 덮어써서 서버가
        # 본문을 통째로 파싱하지 못한다.
        resp = self._session.request(
            "POST",
            url,
            data=data or None,
            files=payload_files or None,
            headers={
                "Authorization": self._make_bearer(token),
                "Accept": "application/json",
                "Content-Type": None,
            },
            # 파일 업로드는 JSON 요청보다 오래 걸린다.
            timeout=60,
        )

        response_body = resp.json() if resp.content else {}

        if not resp.ok:
            error_code = response_body.get("code")
            endpoint = path.split("/")[-1]
            if not is_retry and self._token_manager.should_refresh(resp.status_code, error_code):
                self._token_manager.invalidate()
                return self._multipart_request(path, fields, files, is_retry=True)
            raise SendgoError.from_response(resp.status_code, response_body, endpoint, self._api_version)

        return response_body

    def _make_bearer(self, token: str) -> str:
        if self._api_version == "v2":
            return f"Bearer {token}"
        return "Bearer " + base64.b64encode(token.encode()).decode()
