"""수신거부(080) 번호 조회."""

from __future__ import annotations

from typing import Any

from .http_client import HttpClient


class RejectedNumberService:
    """수신거부 번호 조회. v2 전용, 조회 전용.

    발송 API 가 알아서 제외하지만 **자기 DB 의 수신 상태도 맞춰야** 한다 —
    그러지 않으면 매번 보내고 매번 걸러지는 것을 반복하고, 자기 화면에서는
    여전히 "수신 동의" 로 보인다.

    Example::

        # 증분만 가져간다. 전체를 매번 받으면 번호가 쌓일수록 무거워진다.
        rejected = client.rejected_numbers.list(since="2026-09-01", count=500)
    """

    _RESOURCE = "rejected-numbers"

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        since: str | None = None,
        search: str | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        return self._http.get(
            self._RESOURCE,
            {"since": since, "search": search, "count": count},
        )
