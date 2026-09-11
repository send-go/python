# sendgo-python

> **Python / Django / FastAPI에서 카카오 알림톡, 브랜드메시지, SMS를 가장 쉽게 발송하는 SDK**

[![PyPI version](https://img.shields.io/pypi/v/sendgo-python?logo=pypi)](https://pypi.org/project/sendgo-python/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![Downloads](https://img.shields.io/pypi/dm/python)](https://pypi.org/project/sendgo-python/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

`sendgo-python`은 [Sendgo](https://sendgo.io) 알림 API를 위한 공식 Python SDK입니다.
**`requests` 하나만 의존하며**, 완전한 타입 힌트(Type Hints)를 제공합니다.
Django, FastAPI, Flask, Celery 등 모든 Python 환경에서 사용할 수 있습니다.

---

## 목차

- [Sendgo란?](#sendgo란)
- [주요 기능](#주요-기능)
- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [상세 사용법](#상세-사용법)
  - [카카오 알림톡](#카카오-알림톡)
  - [카카오 친구톡](#카카오-친구톡)
  - [SMS / LMS / MMS](#sms--lms--mms)
- [프레임워크 통합](#프레임워크-통합)
  - [Django](#django)
  - [FastAPI](#fastapi)
  - [Celery 비동기 발송](#celery-비동기-발송)
- [예외 처리](#예외-처리)
- [설정 옵션](#설정-옵션)
- [자주 묻는 질문](#자주-묻는-질문-faq)
- [관련 패키지](#관련-패키지)

---

## Sendgo란?

[Sendgo](https://sendgo.io)는 대한민국 기업과 개발자를 위한 **통합 알림 발송 플랫폼**입니다.

- **카카오 알림톡**: 카카오톡 채널을 통한 정보성 메시지 (주문 확인, 배송 안내, 예약 확인 등)
- **카카오 친구톡**: 마케팅/이벤트 메시지 (쿠폰, 프로모션 등)
- **SMS / LMS / MMS**: 전통적인 문자 메시지
- **자동 대체 발송**: 알림톡 실패 시 SMS로 자동 전환

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| **최소 의존성** | `requests` 하나만 필요 |
| **완전한 타입 힌트** | 모든 파라미터와 반환값에 타입 정의 |
| **스레드 안전 토큰 관리** | `threading.Lock` 기반, 멀티스레드 환경 안전 |
| **토큰 자동 캐싱(50분)** | 매 요청마다 토큰을 발급하지 않음 |
| **401/403 자동 재시도** | 토큰 만료 시 자동 갱신 후 재발송 |
| **다건 동시 발송** | 수신자 리스트로 대량 발송 |
| **예약 발송** | 원하는 시각에 발송 예약 |
| **SMS 자동 대체 발송** | 알림톡 실패 시 SMS로 자동 전환 |
| **v1 / v2 API 지원** | 설정 한 줄로 버전 전환 |

---

## 설치

```bash
pip install sendgo-python
```

또는 `pyproject.toml`:
```toml
[project]
dependencies = ["sendgo-python>=1.0.0"]
```

---

## 빠른 시작

### 1단계 — 환경변수 설정

```bash
# .env
SENDGO_ACCESS_KEY=your_access_key
SENDGO_SECRET_KEY=your_secret_key
SENDGO_KAKAO_SENDER_KEY=your_kakao_key
SENDGO_SMS_SENDER_KEY=your_sms_key
SENDGO_API_VERSION=v2
```

### 2단계 — 클라이언트 초기화

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
```

### 3단계 — 알림톡 전송

```python
client.alimtalk.send(
    template_code="ORDER_CONFIRM_001",
    contacts=[
        {
            "contact": "01012345678",   # 수신자 전화번호 (필수)
            "name":    "홍길동",         # 수신자 이름 (선택)
            "var1":    "ORD-20260723-001",  # 템플릿 변수 #{var1}
            "var2":    "스프링 부트 가이드",  # 템플릿 변수 #{var2}
            "var3":    "29,000원",           # 템플릿 변수 #{var3}
        }
    ],
)
```

---

## 상세 사용법

### 카카오 알림톡

```python
# 다건 발송
client.alimtalk.send(
    template_code="ORDER_CONFIRM_001",
    contacts=[
        {"contact": "01011111111", "name": "홍길동", "var1": "ORD-001"},
        {"contact": "01022222222", "name": "김철수", "var1": "ORD-002"},
        {"contact": "01033333333", "name": "이영희", "var1": "ORD-003"},
    ],
)

# 예약 발송
client.alimtalk.send(
    template_code="PROMO_SUMMER_2026",
    schedule_type="SCHEDULED",
    at="2026-07-28 09:00:00",
    contacts=[{"contact": "01012345678", "var1": "여름 한정 50% 할인"}],
)

# 알림톡 실패 시 SMS 자동 대체 발송
client.alimtalk.send(
    template_code="DELIVERY_START_001",
    contacts=[{"contact": "01012345678", "var1": "ORD-001", "var2": "1234567890"}],
    replace_sms="Y",
    sms_subject="[배송 시작 안내]",
    sms_content="주문하신 상품이 출고되었습니다.\n송장번호: #{var2}",
)
```

### 카카오 친구톡

> ⚠️ **Deprecated — 친구톡은 카카오 정책에 따라 2025-12-31 종료되었습니다.**
> 2026-01-01 부터 친구톡 발송 요청은 카카오 측에서 **브랜드메시지(자유형)** 로 자동 대체 발송됩니다.
> 호출은 계속 성공하며, 자유 본문 타입(`FT`/`FI`/`FW`)을 개별 수신자에게 보내는 경로는
> 현재 이것뿐이므로 기존 코드를 당장 바꿀 필요는 없습니다.
>
> 다음의 경우에는 **브랜드메시지**를 사용하세요.
> - 템플릿 기반 리치 타입 (`FL`/`FC`/`FM`/`FP`/`FA`)
> - 채널 친구가 **아닌** 수신자 (`targeting` = `N` / `I`)
> - 수신 동의한 전체 채널 친구 동보 (`targeting` = `F`)
>
> 메시지 타입은 1:1 대응되며 변환은 서버가 처리합니다 — `FT`→`BT`, `FI`→`BI`, `FW`→`BW`,
> `FL`→`BL`, `FC`→`BC`, `FM`→`BM`, `FP`→`BP`, `FA`→`BA`.

```python
# 텍스트형
client.friendtalk.send(
    content="안녕하세요! 7월 한정 특가 이벤트를 확인해보세요.",
    contacts=[{"contact": "01012345678"}],
)

# 이미지형
client.friendtalk.send(
    message_type="FI",
    content="이번 주 특가 상품을 확인하세요!",
    image_url="https://cdn.example.com/banner.jpg",
    image_link="https://example.com/event",
    contacts=[{"contact": "01012345678"}],
)
```

### SMS / LMS / MMS

```python
# SMS
client.sms.send_sms(
    content="[Sendgo] 인증번호: 123456 (5분 이내 입력)",
    contacts=[{"contact": "01012345678"}],
)

# LMS — 장문 (2,000자 이하)
client.sms.send_lms(
    subject="[중요] 서비스 점검 안내",
    content="""안녕하세요. 서비스 점검이 예정되어 있습니다.

■ 점검 일시: 2026-07-25 02:00 ~ 06:00
■ 영향 범위: 전체 서비스

이용에 불편을 드려 죄송합니다.""",
    contacts=[{"contact": "01012345678"}],
)

# MMS — 이미지 포함
client.sms.send_mms(
    subject="[이벤트] 7월 특가",
    content="이번 달 특가 상품을 확인하세요!",
    contacts=[{"contact": "01012345678"}],
)
```

---

## 브랜드메시지 사용법

브랜드메시지는 친구톡의 후속 채널입니다. 메시지 타입이 친구톡과 1:1 대응되며
(`FT`→`BT`, `FI`→`BI`, `FW`→`BW`, `FL`→`BL`, `FC`→`BC`, `FM`→`BM`, `FP`→`BP`, `FA`→`BA`),
요청에는 **친구톡 코드를 그대로** 넘기고 변환은 서버가 처리합니다.

친구톡과 달리 다음이 가능합니다.

- 채널 친구가 **아닌** 수신자에게 발송 (`targeting: N`)
- 수신 동의한 **전체 채널 친구 동보** 발송 (`targeting: F`, 수신자 목록 불필요)
- 리스트·캐러셀·커머스·동영상 등 **템플릿 기반 리치 메시지**

> v2 전용입니다. 자유 본문 타입(`FT`/`FI`/`FW`)을 개별 수신자에게 보낼 때는 여전히 친구톡 API 를 쓰세요 — 이 엔드포인트는 그 조합에 `NOT_A_BRAND_MESSAGE` 를 반환합니다. 친구톡 요청은 카카오 측에서 브랜드메시지(자유형)로 대체 발송됩니다.

```python
# 단건 발송 — 채널 친구 대상
client.brand_message.send(
    targeting="M",
    message_type="FL",
    friend_template_uuid="9cd5460b-6458-4edc-9b11-c26d3013c340",
    contacts=[{"contact": "01012345678", "var1": "29,000원"}],
)

# 동보 발송 — 수신 동의한 전체 채널 친구 (contacts 불필요)
client.brand_message.broadcast(
    message_type="FW",
    friend_template_uuid="9cd5460b-6458-4edc-9b11-c26d3013c340",
)

# 캠페인 조회 (from 은 예약어이므로 from_ 사용)
campaigns = client.brand_message.campaigns(from_="2026-08-01", count=10)
one = client.brand_message.campaign("1f0a6d0e-6b3b-4f0f-9b2f-2f6f6a1b7c11")
```

---

## 프레임워크 통합

### Django

```python
# settings.py
SENDGO = {
    "access_key":       env("SENDGO_ACCESS_KEY"),
    "secret_key":       env("SENDGO_SECRET_KEY"),
    "kakao_sender_key": env("SENDGO_KAKAO_SENDER_KEY", default=None),
    "sms_sender_key":   env("SENDGO_SMS_SENDER_KEY",   default=None),
    "api_version":      env("SENDGO_API_VERSION", default="v2"),
}
```

```python
# apps/notifications/services.py
from django.conf import settings
from sendgo import Sendgo

_sendgo: Sendgo | None = None

def get_sendgo() -> Sendgo:
    global _sendgo
    if _sendgo is None:
        _sendgo = Sendgo(**settings.SENDGO)
    return _sendgo

def send_order_confirm(phone: str, order_number: str) -> None:
    get_sendgo().alimtalk.send(
        template_code="ORDER_CONFIRM_001",
        contacts=[{"contact": phone, "var1": order_number}],
    )
```

```python
# apps/orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from apps.notifications.services import send_order_confirm

@receiver(post_save, sender=Order)
def on_order_created(sender, instance, created, **kwargs):
    if created:
        send_order_confirm(instance.user.phone, instance.number)
```

### FastAPI

```python
# core/sendgo.py
from functools import lru_cache
from sendgo import Sendgo
from .config import settings

@lru_cache
def get_sendgo() -> Sendgo:
    return Sendgo(
        access_key=settings.SENDGO_ACCESS_KEY,
        secret_key=settings.SENDGO_SECRET_KEY,
        kakao_sender_key=settings.SENDGO_KAKAO_SENDER_KEY,
        api_version="v2",
    )
```

```python
# routers/notify.py
from fastapi import APIRouter, Depends
from sendgo import Sendgo
from core.sendgo import get_sendgo

router = APIRouter(prefix="/api")

@router.post("/notify/order")
async def notify_order(
    phone: str,
    order_number: str,
    sendgo: Sendgo = Depends(get_sendgo),
):
    sendgo.alimtalk.send(
        template_code="ORDER_CONFIRM_001",
        contacts=[{"contact": phone, "var1": order_number}],
    )
    return {"success": True}
```

### Celery 비동기 발송

```python
# tasks/notifications.py
from celery import shared_task
from sendgo import Sendgo, SendgoError
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_alimtalk_task(self, template_code: str, contacts: list[dict]) -> None:
    """카카오 알림톡 비동기 발송 Celery 태스크"""
    sendgo = Sendgo(
        access_key=settings.SENDGO_ACCESS_KEY,
        secret_key=settings.SENDGO_SECRET_KEY,
        kakao_sender_key=settings.SENDGO_KAKAO_SENDER_KEY,
    )
    try:
        sendgo.alimtalk.send(template_code=template_code, contacts=contacts)
    except SendgoError as e:
        logger.error("알림톡 발송 실패: %s [%s]", e, e.error_code)
        if e.error_code not in ("INVALID_TEMPLATE_CODE", "PAYMENT_REQUIRED"):
            raise self.retry(exc=e)
```

```python
# 사용
send_alimtalk_task.delay("ORDER_CONFIRM_001", [{"contact": "01012345678", "var1": "ORD-001"}])
```

---

## 예외 처리

```python
from sendgo import SendgoError

try:
    client.alimtalk.send(
        template_code="ORDER_CONFIRM_001",
        contacts=[{"contact": "01012345678"}],
    )
except SendgoError as e:
    print(f"발송 실패: HTTP {e.status_code} [{e.error_code}]")
    print(f"엔드포인트: {e.endpoint}, API 버전: {e.api_version}")

    match e.error_code:
        case "INVALID_ACCESS_KEY" | "INVALID_SECRET_KEY":
            alert_ops("Sendgo 인증키를 확인하세요.")
        case "INVALID_TEMPLATE_CODE":
            logger.warning("존재하지 않는 템플릿: %s", template_code)
        case "PAYMENT_REQUIRED":
            alert_ops("Sendgo 크레딧이 부족합니다.")
        case "IP_NOT_ALLOWED":
            alert_ops("허용되지 않은 IP에서 요청이 발생했습니다.")
```

---

## 설정 옵션

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `access_key` | `str` | **필수** | — | Sendgo 액세스 키 |
| `secret_key` | `str` | **필수** | — | Sendgo 시크릿 키 |
| `kakao_sender_key` | `str \| None` | 선택 | `None` | 카카오 발신프로필 키 |
| `sms_sender_key` | `str \| None` | 선택 | `None` | SMS 발신자 키 |
| `api_version` | `str` | 선택 | `'v1'` | API 버전 (`v1` \| `v2`) |
| `base_url` | `str` | 선택 | `'https://sendgo.io'` | API 기본 URL |

---

## 자주 묻는 질문 (FAQ)

**Q. 비동기(async/await)를 지원하나요?**
A. 현재 버전은 동기(`requests` 기반)만 지원합니다. FastAPI 등 비동기 환경에서는 `asyncio.get_event_loop().run_in_executor()`로 스레드풀에서 실행하거나, Celery 태스크로 위임하는 방법을 권장합니다. 비동기 버전(`httpx` 기반)은 향후 추가될 예정입니다.

**Q. 멀티스레드 환경에서 안전한가요?**
A. 토큰 관리에 `threading.Lock`을 사용하여 멀티스레드 환경에서도 안전합니다.

**Q. 알림톡 템플릿은 어디서 등록하나요?**
A. [Sendgo 콘솔](https://sendgo.io) → 알림톡 템플릿 → 템플릿 작성 → 카카오 심사 신청 (보통 1~3일 소요)

**Q. 대량 발송 시 rate limit이 있나요?**
A. Sendgo 플랜별로 TPS 제한이 있습니다. [요금 정책](https://sendgo.io/pricing) 참조.

---

## 관련 패키지

| 언어/프레임워크 | 패키지 | GitHub |
|----------------|--------|--------|
| Spring Boot | `io.sendgo:sendgo-spring` | [sendgo-spring-boot-starter](https://github.com/send-go/spring) |
| Node.js | `@sendgo/node` | [sendgo-node](https://github.com/send-go/node) |
| Go | `github.com/send-go/go` | [sendgo-go](https://github.com/send-go/go) |
| 전체 목록 | — | [send-go GitHub 조직](https://github.com/send-go) |

---

## 짧은 URL

짧은 URL 은 메시지 본문의 링크를 줄이고, 그 링크가 실제로 눌렸는지 집계합니다.
문자는 바이트 수가 요금과 직결되므로 링크를 줄이면 그만큼 본문을 더 쓸 수 있습니다.

같은 원본 URL 을 다시 줄이면 **기존 링크가 그대로 반환**됩니다. 캠페인별로 반응을
따로 집계하려면 `forceNew` 로 새 코드를 만드세요.

`deactivate` 는 링크를 삭제하지 않고 리다이렉트만 중지합니다. 이미 발송한 메시지의
링크를 무효화할 때 쓰며, 누적 통계는 남고 이후 접속은 `410 Gone` 이 됩니다.

```python
# 짧은 URL 생성 (v2 전용)
created = sendgo.short_url.create(
    target_url="https://example.com/promotions/summer-sale",
    title="여름 세일 랜딩",
)

code = created["data"]["code"]
link = created["data"]["shortUrl"]

# 반응 통계 — 일별 추이 + 디바이스/유입경로/국가별 분해
# `from` 은 파이썬 예약어이므로 `from_` 을 쓴다
stats = sendgo.short_url.stats(code, from_="2026-08-01")

sendgo.short_url.list(count=10)
sendgo.short_url.show(code)
sendgo.short_url.deactivate(code)   # 리다이렉트만 중지, 통계는 남는다
```

`stats` 는 일별 추이(`daily`)와 디바이스(`byDevice`)·유입경로(`byReferer`)·국가(`byCountry`)별
분해를 반환합니다. 일별 추이는 사전 집계 표에서 읽으므로 클릭이 많아도 응답 시간이 일정합니다.

## 관리 API — 채널·템플릿·발신번호 등록 (v2 전용)

발송은 처음부터 API였지만 **등록과 심사는 콘솔에서만** 되던 것들이 있었습니다.
1.3.0 부터 그 작업도 코드로 처리합니다.

| 서비스 | 하는 일 | 계정 |
| --- | --- | --- |
| `client.kakao_senders` | 카카오 채널 인증·등록·동기화, 브랜드메시지 M/N 신청 | 기업 |
| `client.notice_templates` | 알림톡 템플릿 CRUD, 검수 요청·취소, 승인 취소, 휴면 해제 | 기업 |
| `client.brand_templates` | 브랜드메시지(구 친구톡) 템플릿 CRUD, 동기화, 가져오기 | 기업 |
| `client.sender_registration` | 발신번호 등록 신청, 중복 확인, 유형 안내 | 개인·기업 |
| `client.message_templates` | 문자 상용구 템플릿 CRUD | 개인·기업 |
| `client.kakao_images` | 카카오 이미지 업로드 — 템플릿용 URL 발급 | 기업 |
| `client.rejected_numbers` | 수신거부(080) 번호 조회 | 개인·기업 |
| `client.webhook` | 이벤트 웹훅 구독 — 심사 결과 수신 | 개인·기업 |

> **sendgo.io 콘솔에 들어올 일이 없습니다.** 고객의 채널·발신번호·템플릿을
> 여러분 화면만으로 끝까지 처리할 수 있습니다. 휴대폰 발신번호는 콘솔의 PASS
> 본인인증 대신 **신분증 사본(`identityDocument`)을 받아 sendgo 운영자가 대신
> 심사**합니다.
>
> 사람이 개입하는 지점은 **카카오 채널 인증번호 하나**뿐이고, 그마저도
> 여러분 화면에서 입력받으면 됩니다 — 카카오가 관리자 휴대폰으로 직접 보내는
> 확인이라 없앨 수 없습니다.
>
> 심사가 붙는 것들은 **비동기**입니다. 등록 호출이 성공했다는 건 "접수됐다"는
> 뜻이지 "쓸 수 있다"는 뜻이 아닙니다 — 웹훅을 구독해 결과를 받으세요.

인자는 snake_case 로 씁니다 — SDK 가 camelCase 로 변환해 보냅니다.

### 카카오 채널 등록

```python
# 1단계 — 카카오가 관리자 휴대폰으로 인증번호를 SMS 발송한다 (응답에 번호는 없다)
client.kakao_senders.request_token("@my-channel", "01012345678")

# 2단계 — 사람이 받은 인증번호로 발신프로필 생성
created = client.kakao_senders.create(
    token="123456",
    yellow_id="@my-channel",
    phone_number="01012345678",
    category_code="001001",          # categories() 로 조회
)

kakao_sender_key = created["data"]["sender"]["kakaoSenderKey"]

client.kakao_senders.categories()
client.kakao_senders.list()
client.kakao_senders.sync()                    # 전체 상태 동기화 (하루 한 번 권장)
client.kakao_senders.sync(kakao_sender_key)    # 단건
```

채널이 카카오 쪽에서 차단되면 발송이 조용히 실패하기 시작합니다. `sync()` 를
주기적으로 돌리고 `block: True` 인 채널을 감시하세요.

### 알림톡 템플릿 등록과 검수

```python
created = client.notice_templates.create(
    kakao_sender_key=kakao_sender_key,
    template_name="주문 접수 안내",
    template_content="#{name}님, 주문 #{orderNo}이 접수되었습니다.",
    template_message_type="BA",       # BA 기본형 / EX 부가정보형 / AD 채널추가형 / MI 복합형
    template_emphasize_type="NONE",   # NONE / TEXT / ITEM_LIST / IMAGE
    category_code="001001",

    # sendgo 자체 정책 게이트 — 카카오 심사와 별개다
    message_purpose="order_delivery",
    legal_basis="transaction",
    benefit_origin="none",
    expiry_type="none",

    # 선택 필드는 그냥 이어서 쓰면 된다 (snake_case → camelCase 자동 변환)
    buttons=[{"name": "주문 조회", "linkType": "WL", "linkMo": "https://example.com/orders"}],
)

template_code = created["data"]["template"]["templateCode"]

# 검수 요청 — 증빙이 필요하면 파일도 붙인다 (첨부가 있으면 comment 필수)
client.notice_templates.request_inspection(template_code)

with open("proof.png", "rb") as f:
    client.notice_templates.request_inspection(
        template_code,
        comment="주문 확인 화면 첨부",
        attachments=[("proof.png", f, "image/png")],
    )

# 결과는 비동기다. 웹훅이 없으므로 폴링한다
synced = client.notice_templates.sync(template_code)
synced["data"]["template"]["inspectionStatus"]   # REG → REQ → APR / REJ
```

`opt_in_review_confirmed` · `cta_clear_confirmed` · `policy_confirmed` 는 기본값이
`True` 지만, **내용을 실제로 검토한 뒤에** 그대로 두어야 합니다 — 이 값은 법적
확인의 기록입니다.

정책 필드 조합이 본문과 어긋나면 저장 단계에서 `POLICY_VALIDATION_FAILED` 로
막힙니다. 예외의 `errors["reasons"]` 에 사유가 한국어로 담기니 그대로 사용자에게
보여 주면 됩니다. 여기서 걸리는 문안은 **카카오 심사에서도 거의 반려**되므로,
며칠 기다렸다 반려당하는 것보다 즉시 아는 편이 낫습니다.

```python
client.notice_templates.list(kakao_sender_key=kakao_sender_key, inspection_status="APR")
client.notice_templates.show(template_code)
client.notice_templates.update(template_code, template_content="...")  # 본문이 바뀌면 재검수 필요
client.notice_templates.cancel_inspection(template_code)
client.notice_templates.cancel_approval(template_code)
client.notice_templates.release(template_code)   # 휴면 해제
client.notice_templates.delete(template_code)    # sendgo 목록에서만 삭제된다
client.notice_templates.categories()
```

이미지 템플릿은 `image=` 로 파일을 넘기면 multipart 로 나갑니다.

```python
with open("banner.jpg", "rb") as f:
    client.notice_templates.create(
        kakao_sender_key=kakao_sender_key,
        template_name="이벤트 안내",
        template_emphasize_type="IMAGE",
        image=("banner.jpg", f, "image/jpeg"),
        # ... 나머지 필드 동일
    )
```

> **삭제 동작이 채널마다 다릅니다.** 알림톡 템플릿은 카카오에 삭제 API 가 없어
> sendgo 목록에서만 빠지고 동기화하면 되살아납니다. 브랜드메시지 템플릿은
> 카카오 쪽에서도 실제로 삭제됩니다.

### 브랜드메시지 템플릿

```python
created = client.brand_templates.create(
    kakao_sender_key=kakao_sender_key,
    template_name="여름 세일 안내",
    template_type="FI",              # FT/FI/FW/FL/FC/FM/FP/FA — 서버가 chatBubbleType 으로 변환
    template_content="여름 세일이 시작되었습니다.",
    image_url="https://mud-kage.kakao.com/....jpg",
)

# 동보 발송(targeting="F")에는 변수가 없는 템플릿만 쓸 수 있다
created["data"]["template"]["containsVariables"]

client.brand_templates.list(kakao_sender_key=kakao_sender_key)
client.brand_templates.sync(template_code)
client.brand_templates.import_from_sender(kakao_sender_key)   # 카카오에 있는 템플릿 가져오기
client.brand_templates.delete(template_code)                  # 카카오에서도 삭제된다
```

### 발신번호 등록 신청

```python
# 계정 종류에 맞는 유형과 유형별 필수 서류
client.sender_registration.number_types()

# 형식·중복 미리 확인
check = client.sender_registration.validate("02-1234-5678", "team_main")

with open("csu.pdf", "rb") as f:
    created = client.sender_registration.create(
        sender_alias="고객센터 대표번호",
        sender_number_type="team_main",   # personal_other / team_main / team_other_company
        phone_e164="02-1234-5678",
        files={"csuCertificate": ("csu.pdf", f, "application/pdf")},
        # check["data"]["duplicationReasonRequired"] 가 True 면 필수
        # duplication_reason="부서별 분리 운영",
    )

created["data"]["sender"]["status"]   # PENDING — 운영자 승인 후 SUCCESS

client.sender_registration.list()
client.sender_registration.update(sender_key, sender_alias="새 이름")
client.sender_registration.delete(sender_key)
```

**휴대폰 유형도 API 로 접수할 수 있습니다.** 콘솔의 PASS 본인인증 대신
신분증 사본(`identityDocument`)을 첨부하면 sendgo 운영자가 직접 확인합니다.
이 경로로 접수된 건은 응답의 `identityVerificationMethod` 가 `document` 이고
**자동 승인되지 않습니다** — 운영자 확인 전까지 `PENDING` 입니다.

유형별 필수 서류는 `numberTypes()` 응답의 `requiredDocuments` 로 확인하세요.
반려되면 `rejectionReason` 에 사유가 담깁니다.

### 문자 템플릿

```python
client.message_templates.create(
    message_tran_type="LMS",
    message_tran_subject="주문 안내",   # LMS·MMS 는 필수
    message_tran_msg="주문이 접수되었습니다.",
)

client.message_templates.list(message_type="LMS")
client.message_templates.update(template_key, message_tran_msg="...")
client.message_templates.delete(template_key)
```

### 이벤트 웹훅 — 심사 결과를 밀어 받기

```python
created = client.webhook.subscribe("https://reseller.example.com/hooks/sendgo")

# 시크릿은 이 응답에서 한 번만 나온다. 즉시 저장한다.
secret = created["data"]["secret"]

client.webhook.show()          # 구독 설정 + 마지막 전송 결과
client.webhook.test()          # 배선 확인
client.webhook.unsubscribe()
```

받는 쪽에서는 **원본 바이트**로 서명을 검증합니다.

```python
from sendgo import verify_signature

# Django: request.body / FastAPI: await request.body()
if not verify_signature(request.body, request.headers["X-Sendgo-Signature"], secret):
    return HttpResponse(status=401)

payload = json.loads(request.body)
# payload["event"] — sender.status_changed / notice_template.inspection_status_changed / ...
```

이벤트 목록은 `sendgo.WEBHOOK_EVENTS` 로 확인할 수 있습니다.

### 카카오 이미지 업로드

브랜드메시지 템플릿의 `imageUrl` 은 **카카오가 호스팅하는 URL** 이어야 합니다.

```python
with open("banner.jpg", "rb") as f:
    uploaded = client.kakao_images.upload("default", ("banner.jpg", f, "image/jpeg"))

client.brand_templates.create(
    kakao_sender_key=kakao_sender_key,
    template_name="여름 세일 안내",
    template_type="FI",
    image_url=uploaded["data"]["imageUrl"],
)

client.kakao_images.upload_many("carousel_feed", [slide1, slide2, slide3])
client.kakao_images.types()   # 유형별 필드·최대 개수
```

### 수신거부(080) 동기화

```python
# 증분만 가져간다. 하루 한 번이면 충분하다.
client.rejected_numbers.list(since="2026-09-01", count=500)
```

---

## 변경 사항

### 1.3.0 (2026-09-11)

- **관리 API 추가** — 콘솔에서만 되던 등록·심사를 코드로 처리합니다.
  `client.kakao_senders`(채널 인증·등록·동기화, 브랜드메시지 M/N 신청),
  `client.notice_templates`(알림톡 템플릿 CRUD·검수 요청·승인 취소·휴면 해제),
  `client.brand_templates`(브랜드메시지 템플릿 CRUD·동기화·가져오기),
  `client.sender_registration`(발신번호 등록 신청·중복 확인·유형 안내),
  `client.message_templates`(문자 상용구 템플릿 CRUD).
- `HttpClient` 에 `put()`·`patch()`·`post_multipart()` 를 추가했습니다.
  서류 첨부와 이미지 템플릿은 JSON 으로 보낼 수 없습니다.
- snake_case 인자를 camelCase 로 변환하는 `_payload.camelize()` 를 도입해,
  선택 필드를 그냥 키워드 인자로 이어 쓸 수 있게 했습니다.
- **휴대폰 발신번호도 API 로 접수됩니다.** 콘솔의 PASS 본인인증 대신
  `identityDocument`(신분증 사본)를 첨부하면 sendgo 운영자가 확인합니다.
  이 경로는 자동 승인되지 않고 항상 `PENDING` 으로 시작합니다.
- **이벤트 웹훅** 추가 — 발신번호 승인, 알림톡 검수 결과, 채널 차단,
  브랜드메시지 타겟팅 결과를 구독해 받습니다. 서명은 받은 원본 바이트로
  검증합니다(SDK 에 검증 헬퍼 포함).
- **카카오 이미지 업로드** 추가 — 브랜드메시지 템플릿의 `imageUrl` 은 카카오가
  호스팅하는 URL 이어야 하는데, 그 URL 을 얻는 길이 콘솔에만 있었습니다.
- **수신거부(080) 조회** 추가 — 자기 DB 의 수신 상태를 맞출 수 있습니다.

### 1.2.1 (2026-08-14)

- 레지스트리 목록에 노출되는 패키지 설명에서 친구톡을 브랜드메시지로 교체했습니다.
  npm/PyPI/Packagist/Maven/NuGet/RubyGems 검색 결과에 그대로 찍히는 문자열이라
  종료된 채널을 계속 홍보하고 있었습니다.
- 검색 키워드에 `brand-message` 를 추가했습니다 (`friendtalk` 은 유입 검색어라 유지).

### 1.2.0 (2026-08-14)

- **친구톡 Deprecated 표기** — 친구톡은 카카오 정책에 따라 2025-12-31 종료되었고,
  2026-01-01 부터 발송 요청이 브랜드메시지(자유형)로 자동 대체 발송됩니다.
  관련 API 에 각 언어의 표준 deprecation 표기를 달았습니다.
- 자유 본문 타입(`FT`/`FI`/`FW`)의 개별 발송 경로는 아직 친구톡 API 뿐이라는 점을
  문서에 명시했습니다 — 브랜드메시지 API 는 그 조합에 `NOT_A_BRAND_MESSAGE` 를 반환합니다.
- 브랜드메시지 전환 안내와 메시지 타입 1:1 대응표를 README 에 추가했습니다.

### 1.1.0 (2026-08-11)

- 짧은 URL 추가 — `client.short_url`
- `HttpClient.delete()` 추가
- **버전 단일화** — `__init__.py` 에 하드코딩된 `__version__` 을 제거하고 `importlib.metadata` 로 `pyproject.toml` 값을 읽는다. 두 곳이 어긋나 릴리스가 실패한 적이 있다.

## 라이선스

MIT License © 2026 [Sendgo](https://sendgo.io)

---

*키워드: 카카오 알림톡 Python, 카카오 친구톡 Django, SMS 발송 FastAPI, 알림톡 SDK pip, Python 카카오 API 연동, Django 문자 발송, FastAPI 알림톡, Celery 알림톡 비동기, Sendgo Python SDK*
