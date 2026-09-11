"""알림톡 템플릿 관리 — 등록 · 수정 · 검수 요청."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ._payload import camelize
from .http_client import HttpClient


class NoticeTemplateService:
    """알림톡 템플릿 서비스. v2 전용이며 **기업(Team) 계정 전용**이다.

    템플릿은 만든 즉시 쓸 수 없다. 카카오 검수를 통과해야 한다::

        등록      inspectionStatus=REG   ← 발송 불가
        검수 요청  inspectionStatus=REQ   ← 카카오 심사 중
        승인      inspectionStatus=APR   ← 여기부터 발송 가능
        반려      inspectionStatus=REJ   ← comments 에 사유

    검수 결과는 비동기다. 웹훅이 없으므로 :meth:`sync` 로 폴링한다.

    Example::

        created = client.notice_templates.create(
            kakao_sender_key=kakao_sender_key,
            template_name="주문 접수 안내",
            template_content="#{name}님, 주문 #{orderNo}이 접수되었습니다.",
            template_message_type="BA",
            template_emphasize_type="NONE",
            category_code="001001",
            message_purpose="order_delivery",
            legal_basis="transaction",
            benefit_origin="none",
            expiry_type="none",
        )

        code = created["data"]["template"]["templateCode"]
        client.notice_templates.request_inspection(code)
    """

    _RESOURCE = "notice-templates"

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        kakao_sender_key: str | None = None,
        inspection_status: str | None = None,
        search: str | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """목록 조회."""
        return self._http.get(
            self._RESOURCE,
            {
                "kakaoSenderKey": kakao_sender_key,
                "inspectionStatus": inspection_status,
                "search": search,
                "count": count,
            },
        )

    def show(self, template_code: str) -> dict[str, Any]:
        """상세 조회. ``data.template.policy`` 에 정책 검토 상태가 들어 있다."""
        return self._http.get(self._path(template_code))

    def create(
        self,
        *,
        kakao_sender_key: str,
        template_name: str,
        template_content: str,
        template_message_type: str,
        template_emphasize_type: str,
        category_code: str,
        message_purpose: str,
        legal_basis: str,
        benefit_origin: str,
        expiry_type: str,
        opt_in_review_confirmed: bool = True,
        cta_clear_confirmed: bool = True,
        policy_confirmed: bool = True,
        image: Any = None,
        **extra: Any,
    ) -> dict[str, Any]:
        """템플릿 등록.

        뒤쪽 정책 인자 일곱 개는 sendgo 자체 게이트다. 카카오 심사와 별개이며
        조합이 본문과 어긋나면 ``POLICY_VALIDATION_FAILED`` 로 거절된다.
        세 개의 확인 플래그는 기본값이 ``True`` 지만, **내용을 실제로 검토한
        뒤에** 그대로 두어야 한다 — 이 값은 법적 확인의 기록이다.

        ``extra`` 로 선택 필드를 넘긴다 (``template_title``, ``buttons``,
        ``quick_replies``, ``security_flag`` 등). snake_case 로 쓰면 camelCase 로
        변환된다.

        ``image`` 를 주면 이미지 템플릿으로 multipart 전송한다
        (``template_emphasize_type="IMAGE"``).
        """
        payload = camelize(
            {
                "kakao_sender_key": kakao_sender_key,
                "template_name": template_name,
                "template_content": template_content,
                "template_message_type": template_message_type,
                "template_emphasize_type": template_emphasize_type,
                "category_code": category_code,
                "message_purpose": message_purpose,
                "legal_basis": legal_basis,
                "benefit_origin": benefit_origin,
                "expiry_type": expiry_type,
                "opt_in_review_confirmed": opt_in_review_confirmed,
                "cta_clear_confirmed": cta_clear_confirmed,
                "policy_confirmed": policy_confirmed,
                **extra,
            }
        )

        if image is not None:
            return self._http.post_multipart(self._RESOURCE, payload, {"image": image})

        return self._http.post(self._RESOURCE, payload)

    def update(self, template_code: str, **fields: Any) -> dict[str, Any]:
        """템플릿 수정.

        발신프로필과 템플릿 코드는 바꿀 수 없다. 본문·버튼처럼 카카오에 등록된
        내용이 바뀌면 검수 상태가 되돌아가므로 재검수를 요청해야 한다.
        """
        return self._http.put(self._path(template_code), camelize(fields))

    def delete(self, template_code: str) -> dict[str, Any]:
        """템플릿 삭제.

        **카카오는 템플릿 삭제 API 를 제공하지 않는다.** sendgo 목록에서만
        지워지고 비즈니스 채널 쪽 템플릿은 남는다. 동기화하면 다시 나타난다.
        """
        return self._http.delete(self._path(template_code))

    def sync(self, template_code: str) -> dict[str, Any]:
        """카카오에서 검수 상태와 반려 사유를 다시 읽어 온다."""
        return self._http.post(f"{self._path(template_code)}/sync", {})

    def request_inspection(
        self,
        template_code: str,
        comment: str | None = None,
        attachments: list[Any] | None = None,
    ) -> dict[str, Any]:
        """검수 요청.

        첨부가 있으면 ``comment`` 는 필수다. 정책 검토를 통과하지 못한 템플릿은
        ``POLICY_REVIEW_REQUIRED`` 로 거절되고 ``errors.reasons`` 에 사유가 담긴다.
        """
        path = f"{self._path(template_code)}/inspection"

        if not attachments:
            return self._http.post(path, {"comment": comment} if comment else {})

        return self._http.post_multipart(
            path,
            {"comment": comment},
            {"attachments": attachments},
        )

    def cancel_inspection(self, template_code: str) -> dict[str, Any]:
        """검수 요청 취소. 아직 심사 중(``REQ``)일 때만 통한다."""
        return self._http.delete(f"{self._path(template_code)}/inspection")

    def cancel_approval(self, template_code: str) -> dict[str, Any]:
        """승인 취소. 승인(``APR``)된 템플릿을 되돌린다. 이후에는 발송할 수 없다."""
        return self._http.delete(f"{self._path(template_code)}/approval")

    def release(self, template_code: str) -> dict[str, Any]:
        """휴면 해제. 오래 안 쓴 템플릿이 dormant 로 잠기면 이걸로 깨운다."""
        return self._http.post(f"{self._path(template_code)}/release", {})

    def categories(self, category_code: str | None = None) -> dict[str, Any]:
        """템플릿 카테고리 코드 조회."""
        return self._http.get(
            f"{self._RESOURCE}/categories",
            {"categoryCode": category_code} if category_code else None,
        )

    def _path(self, template_code: str) -> str:
        return f"{self._RESOURCE}/{quote(template_code, safe='')}"
