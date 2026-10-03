from __future__ import annotations
import base64
from typing import Any
from urllib.parse import quote
import requests
from .exceptions import SendgoError


class EmailService:
    """서버 전용 이메일 API. 객체·배열·204(None)·EML(bytes)을 보존합니다."""
    def __init__(self, token_manager=None, base_url="https://sendgo.io", api_version="v2", *, credential=None):
        self._token_manager = token_manager
        self._base_url = base_url.rstrip("/")
        self._api_version = api_version
        self._credential = credential

    @classmethod
    def with_credentials(cls, credential_id: str, password: str, base_url="https://sendgo.io"):
        """앱 키가 아닌 이메일 전용 credential ID/password를 사용합니다."""
        return cls(base_url=base_url, credential=base64.b64encode(f"{credential_id}:{password}".encode()).decode())

    def _request(self, method, path, body=None, query=None, raw=False, retry=False) -> Any:
        if self._api_version != "v2":
            raise ValueError("이메일 API는 api_version='v2'가 필요합니다.")
        basic = self._credential is not None
        prefix = "email-service" if basic else "email"
        auth = f"Basic {self._credential}" if basic else f"Bearer {self._token_manager.get_token()}"
        response = requests.request(method, f"{self._base_url}/api/v2/{prefix}/{path}", json=body,
            params=query, headers={"Authorization": auth, "Accept": "application/json"}, timeout=60, allow_redirects=False)
        ok = 200 <= response.status_code < 300
        if ok and raw:
            return response.content
        try:
            data = response.json() if response.content else None
        except ValueError:
            if ok: raise
            data = {}
        if not ok:
            error = data if isinstance(data, dict) else {}
            if not retry and not basic and response.status_code == 401 and self._token_manager.should_refresh(401, error.get("code")):
                self._token_manager.invalidate()
                return self._request(method, path, body, query, raw, True)
            raise SendgoError.from_response(response.status_code, error, path, "v2")
        return data

    def account(self, query: dict | None = None) -> Any:
        """GET /email/account"""
        return self._request("GET", f"account", None, query, False)

    def request_access(self, body: dict | None = None) -> Any:
        """POST /email/request"""
        return self._request("POST", f"request", body if body is not None else {}, None, False)

    def create_credential(self, body: dict | None = None) -> Any:
        """POST /email/credentials"""
        return self._request("POST", f"credentials", body if body is not None else {}, None, False)

    def credentials(self, query: dict | None = None) -> Any:
        """GET /email/credentials"""
        return self._request("GET", f"credentials", None, query, False)

    def revoke_credential(self, id: str) -> Any:
        """DELETE /email/credentials/{id}"""
        return self._request("DELETE", f"credentials/{quote(str(id), safe='')}", None, None, False)

    def domains(self, query: dict | None = None) -> Any:
        """GET /email/domains"""
        return self._request("GET", f"domains", None, query, False)

    def register_domain(self, body: dict | None = None) -> Any:
        """POST /email/domains"""
        return self._request("POST", f"domains", body if body is not None else {}, None, False)

    def verify_domain(self, id: str, body: dict | None = None) -> Any:
        """POST /email/domains/{id}/verify"""
        return self._request("POST", f"domains/{quote(str(id), safe='')}/verify", body if body is not None else {}, None, False)

    def senders(self, query: dict | None = None) -> Any:
        """GET /email/senders"""
        return self._request("GET", f"senders", None, query, False)

    def request_sender(self, body: dict | None = None) -> Any:
        """POST /email/senders"""
        return self._request("POST", f"senders", body if body is not None else {}, None, False)

    def verify_sender(self, id: str, body: dict | None = None) -> Any:
        """POST /email/senders/{id}/verify"""
        return self._request("POST", f"senders/{quote(str(id), safe='')}/verify", body if body is not None else {}, None, False)

    def request_recipient_verification(self, body: dict | None = None) -> Any:
        """POST /email/recipients/verification"""
        return self._request("POST", f"recipients/verification", body if body is not None else {}, None, False)

    def check_recipients(self, body: dict | None = None) -> Any:
        """POST /email/recipients/check"""
        return self._request("POST", f"recipients/check", body if body is not None else {}, None, False)

    def address_book(self, query: dict | None = None) -> Any:
        """GET /email/address-book"""
        return self._request("GET", f"address-book", None, query, False)

    def sender_profiles(self, query: dict | None = None) -> Any:
        """GET /email/sender-profiles"""
        return self._request("GET", f"sender-profiles", None, query, False)

    def create_sender_profile(self, body: dict | None = None) -> Any:
        """POST /email/sender-profiles"""
        return self._request("POST", f"sender-profiles", body if body is not None else {}, None, False)

    def update_sender_profile(self, id: str, body: dict | None = None) -> Any:
        """PATCH /email/sender-profiles/{id}"""
        return self._request("PATCH", f"sender-profiles/{quote(str(id), safe='')}", body if body is not None else {}, None, False)

    def delete_sender_profile(self, id: str) -> Any:
        """DELETE /email/sender-profiles/{id}"""
        return self._request("DELETE", f"sender-profiles/{quote(str(id), safe='')}", None, None, False)

    def import_address_book(self, body: dict | None = None) -> Any:
        """POST /email/address-book/import"""
        return self._request("POST", f"address-book/import", body if body is not None else {}, None, False)

    def update_address_book_preferences(self, body: dict | None = None) -> Any:
        """POST /email/address-book/preferences"""
        return self._request("POST", f"address-book/preferences", body if body is not None else {}, None, False)

    def send(self, body: dict) -> Any:
        """POST /email/send"""
        return self._request("POST", f"send", body if body is not None else {}, None, False)

    def quote(self, body: dict | None = None) -> Any:
        """POST /email/quote"""
        return self._request("POST", f"quote", body if body is not None else {}, None, False)

    def messages(self, query: dict | None = None) -> Any:
        """GET /email/messages"""
        return self._request("GET", f"messages", None, query, False)

    def message(self, id: str, query: dict | None = None) -> Any:
        """GET /email/messages/{id}"""
        return self._request("GET", f"messages/{quote(str(id), safe='')}", None, query, False)

    def cancel_message(self, id: str, body: dict | None = None) -> Any:
        """POST /email/messages/{id}/cancel"""
        return self._request("POST", f"messages/{quote(str(id), safe='')}/cancel", body if body is not None else {}, None, False)

    def inboxes(self, query: dict | None = None) -> Any:
        """GET /email/inboxes"""
        return self._request("GET", f"inboxes", None, query, False)

    def create_inbox(self, body: dict | None = None) -> Any:
        """POST /email/inboxes"""
        return self._request("POST", f"inboxes", body if body is not None else {}, None, False)

    def update_inbox(self, id: str, body: dict | None = None) -> Any:
        """PATCH /email/inboxes/{id}"""
        return self._request("PATCH", f"inboxes/{quote(str(id), safe='')}", body if body is not None else {}, None, False)

    def inbox_messages(self, id: str, query: dict | None = None) -> Any:
        """GET /email/inboxes/{id}/messages"""
        return self._request("GET", f"inboxes/{quote(str(id), safe='')}/messages", None, query, False)

    def inbox_message(self, id: str, message_id: str, query: dict | None = None) -> Any:
        """GET /email/inboxes/{id}/messages/{messageId}"""
        return self._request("GET", f"inboxes/{quote(str(id), safe='')}/messages/{quote(str(message_id), safe='')}", None, query, False)

    def raw_message(self, id: str, message_id: str, query: dict | None = None) -> Any:
        """GET /email/inboxes/{id}/messages/{messageId}/raw"""
        return self._request("GET", f"inboxes/{quote(str(id), safe='')}/messages/{quote(str(message_id), safe='')}/raw", None, query, True)

    def delete_inbox_message(self, id: str, message_id: str) -> Any:
        """DELETE /email/inboxes/{id}/messages/{messageId}"""
        return self._request("DELETE", f"inboxes/{quote(str(id), safe='')}/messages/{quote(str(message_id), safe='')}", None, None, False)

    def templates(self, query: dict | None = None) -> Any:
        """GET /email/templates"""
        return self._request("GET", f"templates", None, query, False)

    def template(self, id: str, query: dict | None = None) -> Any:
        """GET /email/templates/{id}"""
        return self._request("GET", f"templates/{quote(str(id), safe='')}", None, query, False)

    def create_template(self, body: dict | None = None) -> Any:
        """POST /email/templates"""
        return self._request("POST", f"templates", body if body is not None else {}, None, False)

    def update_template(self, id: str, body: dict | None = None) -> Any:
        """PATCH /email/templates/{id}"""
        return self._request("PATCH", f"templates/{quote(str(id), safe='')}", body if body is not None else {}, None, False)

    def delete_template(self, id: str) -> Any:
        """DELETE /email/templates/{id}"""
        return self._request("DELETE", f"templates/{quote(str(id), safe='')}", None, None, False)

    def contacts(self, query: dict | None = None) -> Any:
        """GET /email/contacts"""
        return self._request("GET", f"contacts", None, query, False)

    def save_contact(self, body: dict | None = None) -> Any:
        """POST /email/contacts"""
        return self._request("POST", f"contacts", body if body is not None else {}, None, False)

    def import_contacts(self, body: dict | None = None) -> Any:
        """POST /email/contacts/import"""
        return self._request("POST", f"contacts/import", body if body is not None else {}, None, False)

    def unsubscribe_contact(self, id: str, body: dict | None = None) -> Any:
        """POST /email/contacts/{id}/unsubscribe"""
        return self._request("POST", f"contacts/{quote(str(id), safe='')}/unsubscribe", body if body is not None else {}, None, False)

    def campaigns(self, query: dict | None = None) -> Any:
        """GET /email/campaigns"""
        return self._request("GET", f"campaigns", None, query, False)

    def create_campaign(self, body: dict | None = None) -> Any:
        """POST /email/campaigns"""
        return self._request("POST", f"campaigns", body if body is not None else {}, None, False)

    def campaign(self, id: str, query: dict | None = None) -> Any:
        """GET /email/campaigns/{id}"""
        return self._request("GET", f"campaigns/{quote(str(id), safe='')}", None, query, False)

    def quote_campaign(self, id: str, body: dict | None = None) -> Any:
        """POST /email/campaigns/{id}/quote"""
        return self._request("POST", f"campaigns/{quote(str(id), safe='')}/quote", body if body is not None else {}, None, False)

    def send_campaign(self, id: str, body: dict | None = None) -> Any:
        """POST /email/campaigns/{id}/send"""
        return self._request("POST", f"campaigns/{quote(str(id), safe='')}/send", body if body is not None else {}, None, False)

    def cancel_campaign(self, id: str, body: dict | None = None) -> Any:
        """POST /email/campaigns/{id}/cancel"""
        return self._request("POST", f"campaigns/{quote(str(id), safe='')}/cancel", body if body is not None else {}, None, False)

    def auth(self, query: dict | None = None) -> Any:
        """GET /email/auth"""
        return self._request("GET", f"auth", None, query, False)
