from __future__ import annotations

from typing import Any, Literal

from .http_client import HttpClient


class SmsService:
    """SMS / LMS / MMS 전송 서비스.

    Example::

        client.sms.send_sms(content="인증번호: 123456", contacts=[{"contact": "01012345678"}])
        client.sms.send_lms(subject="[공지]", content="...", contacts=[...])
    """

    def __init__(self, http: HttpClient, sms_sender_key: str | None) -> None:
        self._http = http
        self._sms_sender_key = sms_sender_key

    def send_sms(self, *, content: str, contacts: list[dict], **kwargs: Any) -> dict:
        """SMS 전송 (90자 이하)."""
        return self.send(content=content, contacts=contacts, message_type="SMS", **kwargs)

    def send_lms(self, *, content: str, contacts: list[dict], **kwargs: Any) -> dict:
        """LMS 전송 (장문, 2,000자 이하)."""
        return self.send(content=content, contacts=contacts, message_type="LMS", **kwargs)

    def send_mms(self, *, content: str, contacts: list[dict], **kwargs: Any) -> dict:
        """MMS 전송 (멀티미디어)."""
        return self.send(content=content, contacts=contacts, message_type="MMS", **kwargs)

    def send(
        self,
        *,
        content: str,
        contacts: list[dict],
        message_type: Literal["SMS", "LMS", "MMS"] = "SMS",
        campaign_type: Literal["MESSAGE", "ADVERTISE", "ELECTION"] = "MESSAGE",
        schedule_type: Literal["DIRECTLY", "SCHEDULED"] = "DIRECTLY",
        at: str | None = None,
        subject: str | None = None,
        files: list | None = None,
    ) -> dict:
        """문자 메시지 전송."""
        body: dict[str, Any] = {
            "campaignType": campaign_type,
            "messageType": message_type,
            "scheduleType": schedule_type,
            "at": at,
            "subject": subject,
            "content": content,
            "files": files or [],
            "contacts": contacts,
            "senderKey": self._sms_sender_key,
        }
        return self._http.post("messages/send", body)
