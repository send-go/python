from __future__ import annotations

from urllib.parse import quote
import requests
from .exceptions import SendgoError


class AccountClient:
    """서버 전용 계정 API. 에이전트 토큰은 자동 갱신하지 않는다."""

    def __init__(self, *, agent_token: str, base_url: str = "https://sendgo.io") -> None:
        if not agent_token or not agent_token.strip():
            raise ValueError("Sendgo: agent_token은 필수입니다.")
        self._agent_token = agent_token
        self._base_url = base_url.rstrip("/")

    def me(self) -> dict:
        """계정 상태와 다음 단계 조회."""
        return self._request("GET", f"")

    def organizations(self) -> dict:
        """조직 목록 조회."""
        return self._request("GET", f"organizations")

    def select_organization(self, organization_id: str | None) -> dict:
        """조직 선택. null은 개인 계정."""
        return self._request("POST", f"organizations/select", {'organizationId': organization_id})

    def api_keys(self) -> dict:
        """현재 조직의 API 키 목록."""
        return self._request("GET", f"api-keys")

    def create_api_key(self, params: dict) -> dict:
        """API 키 발급. secretKey는 이 응답에서만 반환."""
        return self._request("POST", f"api-keys", params)

    def api_key(self, api_key_id: str) -> dict:
        """API 키 상세 조회."""
        return self._request("GET", f"api-keys/{quote(api_key_id, safe='')}")

    def update_api_key(self, api_key_id: str, name: str) -> dict:
        """API 키 이름 변경."""
        return self._request("PATCH", f"api-keys/{quote(api_key_id, safe='')}", {'name': name})

    def delete_api_key(self, api_key_id: str) -> dict:
        """API 키 폐기."""
        return self._request("DELETE", f"api-keys/{quote(api_key_id, safe='')}")

    def issue_token(self, api_key_id: str) -> dict:
        """승인된 API 키의 발송용 토큰 발급."""
        return self._request("POST", f"api-keys/{quote(api_key_id, safe='')}/token", {})

    def allowed_ips(self, api_key_id: str) -> dict:
        """허용 IP 목록과 호출자 IP 조회."""
        return self._request("GET", f"api-keys/{quote(api_key_id, safe='')}/allowed-ips")

    def add_allowed_ip(self, api_key_id: str, params: dict) -> dict:
        """허용 IP 추가. ip와 선택적 description 사용."""
        return self._request("POST", f"api-keys/{quote(api_key_id, safe='')}/allowed-ips", params)

    def delete_allowed_ip(self, api_key_id: str, ip_id: str) -> dict:
        """허용 IP 삭제."""
        return self._request("DELETE", f"api-keys/{quote(api_key_id, safe='')}/allowed-ips/{quote(ip_id, safe='')}")

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        response = requests.request(
            method, f"{self._base_url}/api/v2/account" + (f"/{path}" if path else ""),
            headers={"Authorization": f"Bearer {self._agent_token}", "Accept": "application/json"},
            json=body, timeout=15, allow_redirects=False,
        )
        try:
            data = response.json() if response.content else {}
        except ValueError:
            data = {}
        if not 200 <= response.status_code < 300:
            raise SendgoError.from_response(response.status_code, data, path or "account", "v2")
        return data
