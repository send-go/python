from __future__ import annotations

from .alimtalk import AlimtalkService
from .friendtalk import FriendtalkService
from .http_client import HttpClient
from .sms import SmsService
from .token_manager import TokenManager


class Sendgo:
    """Sendgo Python SDK 메인 클라이언트.

    Example::

        from sendgo import Sendgo

        client = Sendgo(
            access_key="your_access_key",
            secret_key="your_secret_key",
            kakao_sender_key="your_kakao_key",
            sms_sender_key="your_sms_key",
            api_version="v2",
        )

        # 알림톡 전송
        client.alimtalk.send(
            template_code="ORDER_CONFIRM_001",
            contacts=[{"contact": "01012345678", "var1": "ORD-001"}],
        )

        # SMS 전송
        client.sms.send_sms(content="인증번호: 123456", contacts=[{"contact": "01012345678"}])
    """

    def __init__(
        self,
        *,
        access_key: str,
        secret_key: str,
        kakao_sender_key: str | None = None,
        sms_sender_key: str | None = None,
        api_version: str = "v1",
        base_url: str = "https://api.sendgo.io",
    ) -> None:
        token_manager = TokenManager(base_url, access_key, secret_key, api_version)
        http = HttpClient(token_manager, base_url, api_version)

        self.alimtalk   = AlimtalkService(http, kakao_sender_key, sms_sender_key)
        self.friendtalk = FriendtalkService(http, kakao_sender_key, sms_sender_key)
        self.sms        = SmsService(http, sms_sender_key)
