"""템플릿 공용 폴더. v2 전용, 기업 계정 전용."""
from __future__ import annotations
from typing import Any, Literal
from .http_client import HttpClient

class TemplateFolderService:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, *, template_type: Literal["notice", "brand"] | None = None,
             kakao_sender_key: str | None = None) -> dict[str, Any]:
        """폴더 트리와 유형별 템플릿 수를 조회합니다."""
        return self._http.get("template-folders", {"templateType": template_type, "kakaoSenderKey": kakao_sender_key})

    def create(self, *, name: str, parent_uuid: str | None = None) -> dict[str, Any]:
        """루트 또는 하위 폴더를 생성합니다."""
        return self._http.post("template-folders", {"name": name, "parentUuid": parent_uuid})

    def assign(self, *, template_type: Literal["notice", "brand"], kakao_sender_key: str,
               template_codes: list[str], folder_uuid: str | None) -> dict[str, Any]:
        """1~100개 템플릿을 이동합니다. None이면 미분류로 이동합니다."""
        return self._http.patch("template-folders/templates", {
            "templateType": template_type, "kakaoSenderKey": kakao_sender_key,
            "templateCodes": template_codes, "folderUuid": folder_uuid,
        })
