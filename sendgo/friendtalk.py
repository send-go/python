from __future__ import annotations

import warnings
from typing import Any, Literal

from .http_client import HttpClient

FriendtalkMessageType = Literal["FT", "FI", "FW", "FL", "FM", "FC", "FA", "FP"]


class FriendtalkService:
    """카카오 친구톡 전송 서비스.

    .. deprecated::
        친구톡은 카카오 정책에 따라 2025-12-31 종료되었습니다. 2026-01-01 부터
        친구톡 발송 요청은 카카오 측에서 브랜드메시지(자유형)로 자동 대체 발송되므로,
        이 서비스를 호출해도 실제로 나가는 것은 브랜드메시지입니다.
        신규 연동은 :class:`~sendgo.brand_message.BrandMessageService`
        (``client.brand_message``) 를 사용하세요. 다만 자유 본문 타입(FT/FI/FW)을
        개별 수신자에게 보내는 경로는 아직 이 서비스뿐입니다 — 브랜드메시지 API 는
        그 조합에 ``NOT_A_BRAND_MESSAGE`` 를 반환합니다.
        메시지 타입은 1:1 대응됩니다 — FT→BT, FI→BI, FW→BW, FL→BL,
        FC→BC, FM→BM, FP→BP, FA→BA.

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
        """친구톡을 전송합니다.

        .. deprecated::
            2025-12-31 종료. ``client.brand_message.send()`` 를 사용하세요.
        """
        # 파이썬의 DeprecationWarning 은 기본적으로 숨겨지므로 운영 로그를 더럽히지
        # 않으면서, 테스트(-W error)나 개발 모드(-X dev)에서는 확실히 드러난다.
        warnings.warn(
            "친구톡은 2025-12-31 종료되어 2026-01-01 부터 브랜드메시지(자유형)로 "
            "자동 대체 발송됩니다. client.brand_message.send() 를 사용하세요.",
            DeprecationWarning,
            stacklevel=2,
        )
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
