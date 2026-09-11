"""카카오 이미지 업로드 — 브랜드메시지 템플릿에 넣을 URL 발급."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .http_client import HttpClient

#: 파일 하나를 올리고 URL 하나를 받는 유형.
SINGLE_IMAGE_TYPES = (
    "alimtalk",
    "alimtalk_highlight",
    "default",
    "wide",
    "wide_item_list_first",
)

#: 파일 여러 개를 올리고 URL 목록을 받는 유형과 최대 개수.
MULTI_IMAGE_TYPES = {
    "wide_item_list": 4,
    "carousel_feed": 10,
    "carousel_commerce": 11,
}


class KakaoImageService:
    """카카오 이미지 업로드. v2 전용이며 **기업(Team) 계정 전용**이다.

    브랜드메시지 템플릿의 ``imageUrl`` 은 아무 URL 이나 되는 게 아니라
    **카카오가 호스팅하는 URL** 이어야 한다. 그 URL 을 얻는 방법이 이
    업로드뿐이다.

    Example::

        with open("banner.jpg", "rb") as f:
            uploaded = client.kakao_images.upload(
                "default", ("banner.jpg", f, "image/jpeg")
            )

        client.brand_templates.create(
            kakao_sender_key=kakao_sender_key,
            template_name="여름 세일 안내",
            template_type="FI",
            image_url=uploaded["data"]["imageUrl"],
        )
    """

    _RESOURCE = "kakao-images"

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def types(self) -> dict[str, Any]:
        """업로드 가능한 유형과 제약."""
        return self._http.get(f"{self._RESOURCE}/types")

    def upload(self, image_type: str, image: Any) -> dict[str, Any]:
        """단일 이미지 업로드. jpg/png, 2MB 이하. ``data.imageUrl`` 을 받는다."""
        return self._http.post_multipart(self._path(image_type), files={"image": image})

    def upload_many(self, image_type: str, images: list[Any]) -> dict[str, Any]:
        """다중 이미지 업로드. 유형별 최대 개수가 다르다."""
        return self._http.post_multipart(self._path(image_type), files={"images": images})

    def _path(self, image_type: str) -> str:
        return f"{self._RESOURCE}/{quote(image_type, safe='')}"
