"""발신번호(문자) 등록 · 심사 접수."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ._payload import camelize
from .http_client import HttpClient

#: API 로 접수할 수 있는 발신번호 유형 — 전부다.
REGISTRABLE_TYPES = (
    "personal_mobile",
    "personal_other",
    "team_main",
    "team_representative_mobile",
    "team_emp_mobile",
    "team_other_company",
)

#: 신분증 사본(``identityDocument``)이 필요한 유형.
IDENTITY_DOCUMENT_TYPES = (
    "personal_mobile",
    "team_representative_mobile",
    "team_emp_mobile",
)

#: 하위 호환. 이제 전 유형이 등록 가능하다.
API_REGISTRABLE_TYPES = REGISTRABLE_TYPES


class SenderRegistrationService:
    """발신번호 등록 서비스. v2 전용이며 **개인 계정도** 쓸 수 있다.

    등록하면 곧바로 쓸 수 있는 게 아니라 ``PENDING`` 으로 **접수**되고, 운영자
    승인 후 ``SUCCESS`` 가 된다.

    콘솔은 휴대폰 계열(:data:`IDENTITY_DOCUMENT_TYPES`)에 PASS 본인인증을
    요구한다. API 에는 그 화면이 없으므로 **신분증 사본(``identityDocument``)을
    받아 sendgo 운영자가 직접 확인**한다 — 모든 유형을 API 로 접수할 수 있다.

    이 경로로 접수된 건은 응답의 ``identityVerificationMethod`` 가
    ``document`` 이고 **자동 승인되지 않는다.**

    Example::

        check = client.sender_registration.validate("02-1234-5678", "team_main")

        # 유선번호 — 신분증 불필요
        with open("csu.pdf", "rb") as f:
            client.sender_registration.create(
                sender_alias="고객센터 대표번호",
                sender_number_type="team_main",
                phone_e164="02-1234-5678",
                files={"csuCertificate": ("csu.pdf", f, "application/pdf")},
            )

        # 대표자 휴대폰 — PASS 대신 신분증 사본
        with open("csu.pdf", "rb") as csu, open("id.jpg", "rb") as idc:
            client.sender_registration.create(
                sender_alias="대표자 휴대폰",
                sender_number_type="team_representative_mobile",
                phone_e164="01012345678",
                files={
                    "csuCertificate": ("csu.pdf", csu, "application/pdf"),
                    "identityDocument": ("id.jpg", idc, "image/jpeg"),
                },
            )
    """

    _RESOURCE = "senders"

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self) -> dict[str, Any]:
        """목록 조회. 심사 상태(``status``)를 여기서 확인한다."""
        return self._http.get(self._RESOURCE)

    def show(self, sender_key: str) -> dict[str, Any]:
        """상세 조회."""
        return self._http.get(self._path(sender_key))

    def number_types(self) -> dict[str, Any]:
        """계정 종류에 맞는 발신번호 유형과 유형별 필수 서류.

        유형별 ``identityVerification``(``none``/``document``)과 필요한 서류
        목록을 준다.
        """
        return self._http.get(f"{self._RESOURCE}/number-types")

    def validate(self, phone_e164: str, sender_number_type: str) -> dict[str, Any]:
        """등록 전 형식·중복 확인.

        응답의 ``duplicationReasonRequired`` 가 True 면 :meth:`create` 에
        ``duplication_reason`` 을 함께 넣어야 한다.
        """
        return self._http.post(
            f"{self._RESOURCE}/validate",
            {"phoneE164": phone_e164, "senderNumberType": sender_number_type},
        )

    def create(
        self,
        *,
        sender_alias: str,
        sender_number_type: str,
        phone_e164: str,
        files: dict[str, Any],
        **extra: Any,
    ) -> dict[str, Any]:
        """등록 신청. 서류가 붙으므로 multipart 로 나간다.

        ``files`` 에는 최소한 ``csuCertificate``(통신서비스 이용증명원)가 있어야
        한다. 휴대폰 계열은 ``identityDocument``(신분증 사본)가,
        ``team_other_company`` 는 수임·위임 서류가 더 필요하다 —
        :meth:`number_types` 로 확인한다.
        """
        return self._http.post_multipart(
            self._RESOURCE,
            camelize(
                {
                    "sender_alias": sender_alias,
                    "sender_number_type": sender_number_type,
                    "phone_e164": phone_e164,
                    **extra,
                }
            ),
            files,
        )

    def update(
        self,
        sender_key: str,
        *,
        sender_alias: str,
        primary_type: str | None = None,
    ) -> dict[str, Any]:
        """별칭 변경 / 기본 발신 지정. 번호와 심사 상태는 바꿀 수 없다."""
        return self._http.patch(
            self._path(sender_key),
            camelize({"sender_alias": sender_alias, "primary_type": primary_type}),
        )

    def delete(self, sender_key: str) -> dict[str, Any]:
        """삭제. 기본 발신번호를 지우면 남은 번호 중 하나가 기본으로 승계된다."""
        return self._http.delete(self._path(sender_key))

    def _path(self, sender_key: str) -> str:
        return f"{self._RESOURCE}/{quote(sender_key, safe='')}"
