# sendgo-python

> **Sendgo** Python SDK — 카카오 알림톡/친구톡, SMS/LMS/MMS
> Python 3.10+, Django, FastAPI, Flask에서 사용 가능합니다.

[![PyPI](https://img.shields.io/pypi/v/sendgo-python)](https://pypi.org/project/sendgo-python/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)

---

## 빠른 시작 (3단계)

### 1단계 — 설치

```bash
pip install sendgo-python
```

### 2단계 — 환경변수 설정

```env
SENDGO_ACCESS_KEY=your_access_key
SENDGO_SECRET_KEY=your_secret_key
SENDGO_KAKAO_SENDER_KEY=your_kakao_key
SENDGO_SMS_SENDER_KEY=your_sms_key
SENDGO_API_VERSION=v2
```

### 3단계 — 알림톡 전송

```python
import os
from sendgo import Sendgo

client = Sendgo(
    access_key=os.environ["SENDGO_ACCESS_KEY"],
    secret_key=os.environ["SENDGO_SECRET_KEY"],
    kakao_sender_key=os.environ.get("SENDGO_KAKAO_SENDER_KEY"),
    sms_sender_key=os.environ.get("SENDGO_SMS_SENDER_KEY"),
    api_version="v2",
)

client.alimtalk.send(
    template_code="ORDER_CONFIRM_001",
    contacts=[{"contact": "01012345678", "name": "홍길동", "var1": "ORD-001"}],
)
```

---

## 기능별 사용법

### 알림톡

```python
# 다건 발송
client.alimtalk.send(
    template_code="ORDER_CONFIRM_001",
    contacts=[
        {"contact": "01011111111", "var1": "ORD-001"},
        {"contact": "01022222222", "var1": "ORD-002"},
    ],
)

# SMS 대체 발송
client.alimtalk.send(
    template_code="DELIVERY_001",
    contacts=[{"contact": "01012345678", "var1": "ORD-001"}],
    replace_sms="Y",
    sms_subject="[배송 안내]",
    sms_content="상품이 출고되었습니다.",
)

# 예약 발송
client.alimtalk.send(
    template_code="PROMO_001",
    contacts=[{"contact": "01012345678"}],
    schedule_type="SCHEDULED",
    at="2026-04-01 09:00:00",
)
```

### SMS / LMS / MMS

```python
# SMS
client.sms.send_sms(content="인증번호: 123456", contacts=[{"contact": "01012345678"}])

# LMS
client.sms.send_lms(
    subject="[공지사항]",
    content="서비스 점검이 예정되어 있습니다...",
    contacts=[{"contact": "01012345678"}],
)

# MMS
client.sms.send_mms(
    subject="[이벤트]",
    content="이번 주 특가 상품을 확인하세요!",
    contacts=[{"contact": "01012345678"}],
)
```

### 친구톡

```python
client.friendtalk.send(
    content="안녕하세요! 봄맞이 30% 할인 이벤트입니다.",
    contacts=[{"contact": "01012345678"}],
)
```

---

## Django 통합

```python
# settings.py
SENDGO = {
    "access_key": env("SENDGO_ACCESS_KEY"),
    "secret_key": env("SENDGO_SECRET_KEY"),
    "kakao_sender_key": env("SENDGO_KAKAO_SENDER_KEY", default=None),
    "api_version": "v2",
}
```

```python
# services/notification.py
from django.conf import settings
from sendgo import Sendgo

_client = None

def get_sendgo() -> Sendgo:
    global _client
    if _client is None:
        _client = Sendgo(**settings.SENDGO)
    return _client
```

---

## FastAPI 통합

```python
from functools import lru_cache
from sendgo import Sendgo

@lru_cache
def get_sendgo() -> Sendgo:
    return Sendgo(
        access_key=settings.SENDGO_ACCESS_KEY,
        secret_key=settings.SENDGO_SECRET_KEY,
        kakao_sender_key=settings.SENDGO_KAKAO_KEY,
        api_version="v2",
    )

@router.post("/notify")
async def notify(req: NotifyRequest, client: Sendgo = Depends(get_sendgo)):
    client.alimtalk.send(template_code="NOTIFY_001", contacts=[{"contact": req.phone}])
    return {"success": True}
```

---

## 예외 처리

```python
from sendgo import SendgoError

try:
    client.alimtalk.send(...)
except SendgoError as e:
    print(f"발송 실패: status={e.status_code}, code={e.error_code}")
    if e.error_code == "INVALID_TEMPLATE_CODE":
        print("템플릿 코드를 확인하세요.")
    elif e.error_code == "PAYMENT_REQUIRED":
        print("크레딧이 부족합니다.")
```

---

## 라이선스

MIT License © [Sendgo](https://sendgo.io)
