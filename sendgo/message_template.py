"""문자(SMS/LMS/MMS) 상용구 템플릿."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ._payload import camelize
from .http_client import HttpClient


class MessageTemplateService:
    """문자 템플릿 서비스. v2 전용.

    카카오 템플릿과 달리 **검수가 없어** 만들면 바로 쓸 수 있고, 기업 계정이
    아니어도 된다.

    Example::

        client.message_templates.create(
            message_tran_type="LMS",
            message_tran_subject="주문 안내",
            message_tran_msg="주문이 접수되었습니다.",
        )
    """

    _RESOURCE = "message-templates"

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        message_type: str | None = None,
        search: str | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """목록 조회."""
        return self._http.get(
            self._RESOURCE,
            {"messageType": message_type, "search": search, "count": count},
        )

    def show(self, template_key: str) -> dict[str, Any]:
        """상세 조회."""
        return self._http.get(self._path(template_key))

    def create(
        self,
        *,
        message_tran_type: str,
        message_tran_msg: str,
        message_tran_subject: str | None = None,
        is_favorite: bool = False,
    ) -> dict[str, Any]:
        """등록. LMS·MMS 는 ``message_tran_subject`` 가 필수다."""
        return self._http.post(
            self._RESOURCE,
            camelize(
                {
                    "message_tran_type": message_tran_type,
                    "message_tran_msg": message_tran_msg,
                    "message_tran_subject": message_tran_subject,
                    "is_favorite": is_favorite,
                }
            ),
        )

    def update(self, template_key: str, **fields: Any) -> dict[str, Any]:
        """수정."""
        return self._http.put(self._path(template_key), camelize(fields))

    def delete(self, template_key: str) -> dict[str, Any]:
        """삭제 (소프트 삭제 — 목록에서만 사라진다)."""
        return self._http.delete(self._path(template_key))

    def _path(self, template_key: str) -> str:
        return f"{self._RESOURCE}/{quote(template_key, safe='')}"
