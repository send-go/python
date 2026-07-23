from __future__ import annotations

from typing import Literal

from .http_client import HttpClient


class AlimtalkService:
    """카카오 알림톡 전송 서비스.

    Example::

        client.alimtalk.send(
            template_code="ORDER_CONFIRM_001",
            contacts=[{"contact": "01012345678", "var1": "ORD-001"}],
        )
    """

    def __init__(self, http: HttpClient, kakao_sender_key: str | None, sms_sender_key: str | None) -> None:
        self._http = http
        self._kakao_sender_key = kakao_sender_key
        self._sms_sender_key = sms_sender_key

    def send(
        self,
        *,
        template_code: str,
        contacts: list[dict],
        schedule_type: Literal["DIRECTLY", "SCHEDULED"] = "DIRECTLY",
        at: str | None = None,
        replace_sms: Literal["Y", "N"] = "N",
        sms_subject: str | None = None,
        sms_content: str | None = None,
    ) -> dict:
        """알림톡을 전송합니다.

        Args:
            template_code: 승인된 알림톡 템플릿 코드 (필수)
            contacts: 수신자 목록. 각 dict에 contact(필수), name, var1~var8 포함 가능
            schedule_type: 발송 유형 (DIRECTLY | SCHEDULED)
            at: 예약 발송 시각 (예: "2026-04-01 09:00:00")
            replace_sms: 알림톡 실패 시 SMS 대체 발송 여부
            sms_subject: 대체 SMS 제목
            sms_content: 대체 SMS 내용
        """
        body: dict = {
            "at": at,
            "scheduleType": schedule_type,
            "templateCode": template_code,
            "replaceSms": replace_sms,
            "smsSubject": sms_subject if replace_sms == "Y" else None,
            "smsContent": sms_content if replace_sms == "Y" else None,
            "contacts": contacts,
            "kakaoSenderKey": self._kakao_sender_key,
            "senderKey": self._sms_sender_key,
        }
        return self._http.post("notices/send", body)
