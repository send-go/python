"""짧은 URL — 메시지에 넣는 링크를 줄이고 클릭 반응을 집계한다."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .http_client import HttpClient


class ShortUrlService:
    """짧은 URL 서비스. v2 전용이다.

    Example:
        created = client.short_url.create(
            target_url="https://example.com/promotions/summer-sale",
            title="여름 세일 랜딩",
        )

        # created["data"]["shortUrl"] 를 문자/알림톡 본문에 넣는다.
        stats = client.short_url.stats(created["data"]["code"])
    """

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        target_url: str,
        title: str | None = None,
        expires_at: str | None = None,
        force_new: bool = False,
    ) -> dict[str, Any]:
        """짧은 URL 을 만든다.

        같은 원본 URL 을 다시 줄이면 기존 링크가 그대로 반환된다.
        캠페인별로 반응을 분리해 집계하려면 ``force_new=True`` 를 쓴다.
        """
        body: dict[str, Any] = {"targetUrl": target_url, "forceNew": force_new}

        if title is not None:
            body["title"] = title
        if expires_at is not None:
            body["expiresAt"] = expires_at

        return self._http.post("short-urls", body)

    def list(
        self,
        *,
        from_: str | None = None,
        to: str | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """목록 조회. ``from`` 은 파이썬 예약어이므로 ``from_`` 을 쓴다."""
        params = {"from": from_, "to": to, "count": count}

        return self._http.get("short-urls", {k: v for k, v in params.items() if v is not None})

    def show(self, code: str) -> dict[str, Any]:
        """상세 조회."""
        return self._http.get(f"short-urls/{quote(code, safe='')}")

    def stats(
        self,
        code: str,
        *,
        from_: str | None = None,
        to: str | None = None,
    ) -> dict[str, Any]:
        """반응 통계. 일별 추이와 디바이스/유입경로/국가별 분해를 반환한다."""
        params = {"from": from_, "to": to}

        return self._http.get(
            f"short-urls/{quote(code, safe='')}/stats",
            {k: v for k, v in params.items() if v is not None},
        )

    def deactivate(self, code: str) -> dict[str, Any]:
        """리다이렉트를 중지한다.

        링크는 삭제되지 않고 누적 통계도 남는다. 이후 그 링크로 들어오면
        410 Gone 이 반환된다.
        """
        return self._http.delete(f"short-urls/{quote(code, safe='')}")
