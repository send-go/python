from __future__ import annotations

from .alimtalk import AlimtalkService
from .brand_message import BrandMessageService
from .brand_template import BrandTemplateService
from .friendtalk import FriendtalkService
from .http_client import HttpClient
from .kakao_image import KakaoImageService
from .kakao_sender import KakaoSenderService
from .message_template import MessageTemplateService
from .notice_template import NoticeTemplateService
from .rejected_number import RejectedNumberService
from .sender_registration import SenderRegistrationService
from .short_url import ShortUrlService
from .sms import SmsService
from .token_manager import TokenManager
from .webhook import WebhookService


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

        # ------------------------------------------------------ 관리 API (v2)
        # 콘솔에서만 되던 등록·심사. 발송과 달리 대부분 즉시 완료되지 않는다 —
        # 등록 성공은 "접수됨"이지 "사용 가능"이 아니다. 결과는 웹훅으로 받는다.
        #
        # 사람이 개입하는 지점은 카카오 채널 인증번호 하나뿐이고, 그마저도
        # 여러분 화면에서 끝난다 — request_token() 이 채널 관리자 휴대폰으로
        # SMS 를 보내고, 사용자가 입력한 코드를 create() 가 받는다. 휴대폰
        # 발신번호는 PASS 대신 신분증 사본을 첨부해 접수하면 sendgo 가 대신
        # 심사한다.
        self.kakao_senders       = KakaoSenderService(http)
        self.notice_templates    = NoticeTemplateService(http)
        self.brand_templates     = BrandTemplateService(http)
        self.sender_registration = SenderRegistrationService(http)
        self.message_templates   = MessageTemplateService(http)
        self.kakao_images        = KakaoImageService(http)
        self.rejected_numbers    = RejectedNumberService(http)
        self.webhook             = WebhookService(http)
