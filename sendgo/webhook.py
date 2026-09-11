"""이벤트 웹훅 구독 — 등록·심사 결과를 밀어 받는다."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

from .http_client import HttpClient

#: 구독할 수 있는 이벤트.
WEBHOOK_EVENTS = (
    "sender.status_changed",
    "notice_template.inspection_status_changed",
    "kakao_sender.status_changed",
    "kakao_sender.brand_message_status_changed",
)


def verify_signature(raw_body: bytes | str, signature: str, secret: str) -> bool:
    """수신한 웹훅의 서명을 검증한다.

    ``raw_body`` 는 **받은 바이트 그대로**여야 한다. 파싱한 뒤 다시 인코딩한
    값으로 계산하면 키 순서나 이스케이프 차이로 검증이 깨진다.
    Django 라면 ``request.body``, FastAPI 라면 ``await request.body()`` 다.
    """
    payload = raw_body.encode() if isinstance(raw_body, str) else raw_body
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected, signature)


class WebhookService:
    """웹훅 구독 서비스. v2 전용.

    심사는 비동기라 폴링 말고는 방법이 없었다. 구독해 두면 상태가 바뀔 때마다
    도착한다.

    Example::

        created = client.webhook.subscribe("https://reseller.example.com/hooks/sendgo")

        # 시크릿은 이 응답에서 한 번만 나온다. 즉시 저장한다.
        secret = created["data"].get("secret")
    """

    _RESOURCE = "webhook"

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def show(self) -> dict[str, Any]:
        """현재 구독 설정. 마지막 전송 결과(``lastStatus``)도 함께 온다."""
        return self._http.get(self._RESOURCE)

    def subscribe(
        self,
        url: str,
        *,
        secret: str | None = None,
        events: list[str] | None = None,
        enabled: bool = True,
    ) -> dict[str, Any]:
        """구독 생성·수정.

        ``secret`` 을 생략하면 서버가 만들어 **이 응답에서 한 번만** 돌려준다.
        이미 시크릿이 있는 상태에서 생략하면 기존 값을 유지한다 — URL 만
        바꾸는 호출이 서명 키를 날리지 않는다.

        ``events`` 가 None 이면 전체 구독이다.
        """
        body: dict[str, Any] = {"url": url, "enabled": enabled}

        if secret is not None:
            body["secret"] = secret
        if events is not None:
            body["events"] = events

        return self._http.put(self._RESOURCE, body)

    def test(self) -> dict[str, Any]:
        """테스트 이벤트 발송. 구독 목록과 무관하게 도착한다."""
        return self._http.post(f"{self._RESOURCE}/test", {})

    def unsubscribe(self) -> dict[str, Any]:
        """구독 해지."""
        return self._http.delete(self._RESOURCE)
