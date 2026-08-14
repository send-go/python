from __future__ import annotations

from .alimtalk import AlimtalkService
from .brand_message import BrandMessageService
from .friendtalk import FriendtalkService
from .http_client import HttpClient
from .short_url import ShortUrlService
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
        base_url: str = "https://sendgo.io",
    ) -> None:
        token_manager = TokenManager(base_url, access_key, secret_key, api_version)
        http = HttpClient(token_manager, base_url, api_version)

        self.alimtalk      = AlimtalkService(http, kakao_sender_key, sms_sender_key)
        # Deprecated — 친구톡은 2025-12-31 종료. brand_message 를 사용한다.
        self.friendtalk    = FriendtalkService(http, kakao_sender_key, sms_sender_key)
        # 카카오 브랜드메시지 — 친구톡의 후속 채널. v2 전용.
        self.brand_message = BrandMessageService(http, kakao_sender_key, sms_sender_key)
        # 짧은 URL — 링크 단축과 클릭 반응 분석. v2 전용.
        self.short_url     = ShortUrlService(http)
        self.sms           = SmsService(http, sms_sender_key)
