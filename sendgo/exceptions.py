from __future__ import annotations


class SendgoError(Exception):
    """Sendgo API 호출 실패 시 발생하는 예외."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 0,
        error_code: str | None = None,
        endpoint: str = "",
        api_version: str = "",
        response_body: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.endpoint = endpoint
        self.api_version = api_version
        self.response_body = response_body or {}

    @classmethod
    def from_response(
        cls,
        status: int,
        body: dict,
        endpoint: str,
        api_version: str,
    ) -> "SendgoError":
        error_code = body.get("code")
        error_message = body.get("message", "Unknown error")
        msg = f"HTTP {status}"
        if error_code:
            msg += f" [{error_code}]"
        msg += f" {error_message}"
        return cls(
            msg,
            status_code=status,
            error_code=error_code,
            endpoint=endpoint,
            api_version=api_version,
            response_body=body,
        )

    def __repr__(self) -> str:
        return (
            f"SendgoError(status={self.status_code}, "
            f"error_code={self.error_code!r}, "
            f"endpoint={self.endpoint!r})"
        )
