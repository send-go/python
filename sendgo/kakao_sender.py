"""카카오 발신프로필(채널) 관리 — 등록 · 동기화 · 브랜드메시지 타겟팅 신청."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .http_client import HttpClient


class KakaoSenderService:
    """카카오 채널 관리 서비스. v2 전용이며 **기업(Team) 계정 전용**이다.

    채널 등록은 두 단계다. 카카오가 인증번호를 채널 관리자 **휴대폰으로 SMS
    발송**하므로 완전 무인 자동화는 불가능하다 — 사람이 문자를 받아
    :meth:`create` 에 넣어야 한다.

    Example::

        # 1단계 — 관리자 휴대폰으로 인증번호 발송 (응답에 번호는 없다)
        client.kakao_senders.request_token("@my-channel", "01012345678")

        # 2단계 — 사람이 받은 인증번호로 발신프로필 생성
        created = client.kakao_senders.create(
            token="123456",
            yellow_id="@my-channel",
            phone_number="01012345678",
            category_code="001001",
        )

        kakao_sender_key = created["data"]["sender"]["kakaoSenderKey"]
    """

    _RESOURCE = "kakao-senders"

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def request_token(self, yellow_id: str, phone_number: str) -> dict[str, Any]:
        """1단계 — 채널 인증번호 발송.

        응답에 인증번호는 들어있지 않다. 카카오가 ``phone_number`` 로 SMS 를 보낸다.
        """
        return self._http.post(
            f"{self._RESOURCE}/token",
            {"yellowId": yellow_id, "phoneNumber": phone_number},
        )

    def create(
        self,
        *,
        token: str,
        yellow_id: str,
        phone_number: str,
        category_code: str,
    ) -> dict[str, Any]:
        """2단계 — 발신프로필 등록.

        이미 등록된 채널을 다시 등록해도 오류가 아니다. 카카오가 같은 senderKey 를
        돌려주고 서버가 기존 행을 갱신한다.
        """
        return self._http.post(
            self._RESOURCE,
            {
                "token": token,
                "yellowId": yellow_id,
                "phoneNumber": phone_number,
                "categoryCode": category_code,
            },
        )

    def list(self) -> dict[str, Any]:
        """목록 조회."""
        return self._http.get(self._RESOURCE)

    def show(self, kakao_sender_key: str) -> dict[str, Any]:
        """상세 조회."""
        return self._http.get(f"{self._RESOURCE}/{quote(kakao_sender_key, safe='')}")

    def categories(self, category_code: str | None = None) -> dict[str, Any]:
        """카테고리 조회. 등록 시 ``category_code`` 로 넣을 값이다."""
        return self._http.get(
            f"{self._RESOURCE}/categories",
            {"categoryCode": category_code} if category_code else None,
        )

    def sync(self, kakao_sender_key: str | None = None) -> dict[str, Any]:
        """상태 동기화. 키를 주면 단건, 없으면 팀 전체.

        채널이 카카오 쪽에서 차단·휴면되면 발송이 조용히 실패하기 시작한다.
        그 사실을 먼저 알 방법은 이 호출뿐이므로 하루 한 번 정도 돌리는 게 좋다.
        """
        path = (
            f"{self._RESOURCE}/{quote(kakao_sender_key, safe='')}/sync"
            if kakao_sender_key
            else f"{self._RESOURCE}/sync"
        )
        return self._http.post(path, {})

    def upload_brand_message_evidence(
        self,
        kakao_sender_key: str,
        evidence: Any,
    ) -> dict[str, Any]:
        """브랜드메시지 M 신청에 필요한 광고성 정보 수신동의 증적자료 업로드.

        jpg/png, 5MB 이하. ``evidence`` 는 ``requests`` 가 받는 형태를 그대로 쓴다
        — 열린 파일 객체나 ``(filename, fileobj)`` 튜플.
        """
        return self._http.post_multipart(
            f"{self._RESOURCE}/{quote(kakao_sender_key, safe='')}/brand-message/evidence",
            files={"evidence": evidence},
        )

    def apply_brand_message_targeting(
        self,
        kakao_sender_key: str,
        target_type: str,
    ) -> dict[str, Any]:
        """브랜드메시지 ``M``(마케팅) / ``N``(정보성) 사용 신청.

        결과는 즉시 확정되지 않는다. 발신프로필의 ``brandMessageStatus`` 로 확인한다.
        """
        return self._http.post(
            f"{self._RESOURCE}/{quote(kakao_sender_key, safe='')}/brand-message/apply",
            {"targetType": target_type},
        )
