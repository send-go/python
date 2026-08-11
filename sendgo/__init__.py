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
try:
    from importlib.metadata import PackageNotFoundError, version as _pkg_version

    # 버전은 pyproject.toml 이 단일 출처다. 여기에 값을 또 적으면
    # 릴리스마다 두 곳을 맞춰야 하고, 실제로 어긋난 적이 있다.
    __version__ = _pkg_version("sendgo-python")
except PackageNotFoundError:  # 설치되지 않은 소스 트리에서 import 한 경우
    __version__ = "0.0.0.dev0"
