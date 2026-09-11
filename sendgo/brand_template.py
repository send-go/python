"""브랜드메시지(구 친구톡) 템플릿 관리."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from ._payload import camelize
from .http_client import HttpClient


class BrandTemplateService:
    """브랜드메시지 템플릿 서비스. v2 전용이며 **기업(Team) 계정 전용**이다.

    알림톡 템플릿과 달리 **검수 요청 단계가 없다.** 등록하면 카카오가 바로
    상태를 돌려주고 그 값이 ``status`` 로 나온다.

    ``template_type`` 은 친구톡 표기(``FT``/``FI``/``FW``/``FL``/``FC``/``FM``/
    ``FP``/``FA``)를 그대로 쓴다 — 서버가 chatBubbleType 으로 변환한다.

    Example::

        created = client.brand_templates.create(
            kakao_sender_key=kakao_sender_key,
            template_name="여름 세일 안내",
            template_type="FI",
            template_content="여름 세일이 시작되었습니다.",
            image_url="https://mud-kage.kakao.com/....jpg",
        )

        # 동보 발송(targeting="F")에는 변수가 없는 템플릿만 쓸 수 있다
        created["data"]["template"]["containsVariables"]
    """

    _RESOURCE = "brand-templates"

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        kakao_sender_key: str | None = None,
        search: str | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """목록 조회."""
        return self._http.get(
            self._RESOURCE,
            {"kakaoSenderKey": kakao_sender_key, "search": search, "count": count},
        )

    def show(self, template_code: str) -> dict[str, Any]:
        """상세 조회. sendgo 코드(``KFT-...``)와 카카오 브랜드 템플릿 코드 둘 다 받는다."""
        return self._http.get(self._path(template_code))

    def create(
        self,
        *,
        kakao_sender_key: str,
        template_name: str,
        template_type: str,
        **extra: Any,
    ) -> dict[str, Any]:
        """템플릿 등록. 선택 필드는 ``extra`` 로 넘긴다 (snake_case 자동 변환)."""
        return self._http.post(
            self._RESOURCE,
            camelize(
                {
                    "kakao_sender_key": kakao_sender_key,
                    "template_name": template_name,
                    "template_type": template_type,
                    **extra,
                }
            ),
        )

    def update(self, template_code: str, **fields: Any) -> dict[str, Any]:
        """템플릿 수정. 발신프로필은 바꿀 수 없다."""
        return self._http.put(self._path(template_code), camelize(fields))

    def delete(self, template_code: str) -> dict[str, Any]:
        """템플릿 삭제. 알림톡과 달리 카카오 쪽에서도 실제로 삭제된다."""
        return self._http.delete(self._path(template_code))

    def sync(self, template_code: str) -> dict[str, Any]:
        """동기화. 카카오 쪽에서 이미 삭제됐으면 로컬에서도 제거하고
        ``data.deleted: True`` 를 반환한다."""
        return self._http.post(f"{self._path(template_code)}/sync", {})

    def import_from_sender(self, kakao_sender_key: str) -> dict[str, Any]:
        """발신프로필 단위 가져오기 — 카카오 쪽에 이미 있는 템플릿을 들여온다.

        (``import`` 는 예약어라 메서드 이름에 쓸 수 없다.)
        """
        return self._http.post(
            f"{self._RESOURCE}/import",
            {"kakaoSenderKey": kakao_sender_key},
        )

    def _path(self, template_code: str) -> str:
        return f"{self._RESOURCE}/{quote(template_code, safe='')}"
