from __future__ import annotations

from typing import Any, Literal

from .http_client import HttpClient

FriendtalkMessageType = Literal["FT", "FI", "FW", "FL", "FM", "FC", "FA", "FP"]


class FriendtalkService:
    """카카오 친구톡 전송 서비스.

    Example::

        client.friendtalk.send(
            content="안녕하세요! 이번 주 특가 이벤트입니다.",
            contacts=[{"contact": "01012345678"}],
        )
    """

    def __init__(self, http: HttpClient, kakao_sender_key: str | None, sms_sender_key: str | None) -> None:
        self._http = http
        self._kakao_sender_key = kakao_sender_key
        self._sms_sender_key = sms_sender_key

    def send(
        self,
        *,
        content: str,
        contacts: list[dict],
        message_type: FriendtalkMessageType = "FT",
        schedule_type: Literal["DIRECTLY", "SCHEDULED"] = "DIRECTLY",
        at: str | None = None,
        buttons: list[dict] | None = None,
        image_url: str | None = None,
        image_link: str | None = None,
        ad_flag: Literal["Y", "N"] = "Y",
        wide: Literal["Y", "N"] = "N",
        adult: Literal["Y", "N"] = "N",
        header: str | None = None,
        replace_sms: Literal["Y", "N"] = "N",
        sms_subject: str | None = None,
        sms_content: str | None = None,
    ) -> dict:
        """친구톡을 전송합니다."""
        body: dict[str, Any] = {
            "at": at,
            "scheduleType": schedule_type,
            "messageType": message_type,
            "content": content,
            "buttons": buttons or [],
            "image": None,
            "imageUrl": image_url,
            "imageLink": image_link,
            "adFlag": ad_flag,
            "wide": wide,
            "adult": adult,
            "header": header,
            "replaceSms": replace_sms,
            "smsSubject": sms_subject if replace_sms == "Y" else None,
            "smsContent": sms_content if replace_sms == "Y" else None,
            "contacts": contacts,
            "kakaoSenderKey": self._kakao_sender_key,
            "senderKey": self._sms_sender_key,
        }
        return self._http.post("friends/send", body)
