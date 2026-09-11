"""요청 페이로드 헬퍼.

Python 쪽 인자는 snake_case, Sendgo API 는 camelCase 다. 서비스마다 매핑을
손으로 적으면 필드가 늘 때마다 빠뜨리는 곳이 생기므로 한 곳에서 변환한다.
"""

from __future__ import annotations

from typing import Any

# 자동 변환이 틀리는 예외들. `additional_content` 는 서버가 그대로 받는다.
_KEEP_AS_IS = {"additional_content"}


def to_camel(key: str) -> str:
    """`template_name` → `templateName`. 이미 camelCase 면 그대로 둔다."""
    if key in _KEEP_AS_IS or "_" not in key:
        return key

    head, *rest = key.split("_")
    return head + "".join(part[:1].upper() + part[1:] for part in rest)


def camelize(payload: dict[str, Any], *, drop_none: bool = True) -> dict[str, Any]:
    """키를 camelCase 로 바꾸고, 기본적으로 ``None`` 값을 걷어낸다.

    ``None`` 을 남기면 서버가 "빈 값으로 덮어쓰기"로 읽어 기존 값을 지운다.
    명시적으로 비우려면 빈 문자열을 넘긴다.
    """
    return {
        to_camel(key): value
        for key, value in payload.items()
        if not (drop_none and value is None)
    }
