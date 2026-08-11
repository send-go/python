"""
Sendgo Python SDK — 카카오 알림톡/친구톡, SMS/LMS/MMS

사용법:
    from sendgo import Sendgo

    client = Sendgo(
        access_key="your_access_key",
        secret_key="your_secret_key",
        kakao_sender_key="your_kakao_key",
        sms_sender_key="your_sms_key",
        api_version="v2",
    )

    client.alimtalk.send(
        template_code="ORDER_CONFIRM_001",
        contacts=[{"contact": "01012345678", "var1": "ORD-001"}],
    )
"""

from .brand_message import BrandMessageService
from .short_url import ShortUrlService
from .client import Sendgo
from .exceptions import SendgoError

__all__ = ["Sendgo", "SendgoError", "BrandMessageService", "ShortUrlService"]
__version__ = "1.1.0"
