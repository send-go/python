from __future__ import annotations

from typing import Any, Literal

from .http_client import HttpClient

BrandMessageType = Literal["FT", "FI", "FW", "FL", "FM", "FC", "FA", "FP"]
BrandMessageTargeting = Literal["M", "N", "I", "F"]


class BrandMessageService:
    """카카오 브랜드메시지 전송 서비스.

    브랜드메시지는 친구톡의 후속 채널로, 메시지 타입이 친구톡과 1:1 대응됩니다
    (FT→BT, FI→BI, FW→BW, FL→BL, FC→BC, FM→BM, FP→BP, FA→BA).
    ``message_type`` 에는 친구톡 코드를 그대로 넘기고, 변환은 서버가 처리합니다.

    친구톡과 달리 채널 친구가 아닌 수신자에게도 보낼 수 있고(``targeting="N"``),
    수신 동의한 전체 채널 친구에게 동보 발송할 수 있습니다(``targeting="F"``).

    Example::

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
    """

    def __init__(self, http: HttpClient, kakao_sender_key: str | None, sms_sender_key: str | None) -> None:
        self._http = http
        self._kakao_sender_key = kakao_sender_key
        self._sms_sender_key = sms_sender_key

    def send(
        self,
        *,
        friend_template_uuid: str,
        message_type: BrandMessageType = "FT",
        targeting: BrandMessageTargeting = "M",
        contacts: list[dict] | None = None,
        content: str | None = None,
        schedule_type: Literal["DIRECTLY", "SCHEDULED"] = "DIRECTLY",
        at: str | None = None,
        buttons: list[dict] | None = None,
        image_url: str | None = None,
        image_link: str | None = None,
        ad_flag: Literal["Y", "N"] = "Y",
        adult: Literal["Y", "N"] = "N",
        push_alarm: Literal["Y", "N"] = "Y",
        header: str | None = None,
        coupon: dict | None = None,
        item: dict | None = None,
        commerce: dict | None = None,
        list_: list[dict] | None = None,
        head: dict | None = None,
        tail: dict | None = None,
        video: dict | None = None,
        additional_content: str | None = None,
        friend_group_key: str | None = None,
        replace_sms: Literal["Y", "N"] = "N",
        sms_subject: str | None = None,
        sms_content: str | None = None,
        reject_service_id: str | None = None,
        webhooks: list[str] | None = None,
    ) -> dict:
        """브랜드메시지를 전송합니다.

        ``targeting`` 이 ``"M"`` / ``"N"`` / ``"I"`` 이면 ``contacts`` 가 필요하고
        응답 ``data`` 에 발송 건수(``sentCount``)가 담깁니다. ``"F"`` 는 동보 발송이라
        ``contacts`` 없이 접수 여부(``accepted``)만 반환됩니다 — 그 경우
        :meth:`broadcast` 가 더 명확합니다.

        ``list_`` 는 파이썬 내장 ``list`` 와 충돌을 피하기 위한 이름이며,
        요청에는 ``list`` 로 전송됩니다.
        """
        body: dict[str, Any] = {
            "at": at,
            "scheduleType": schedule_type,
            "targeting": targeting,
            "messageType": message_type,
            "friendTemplateUuid": friend_template_uuid,
            "content": content,
            "buttons": buttons or [],
            "imageUrl": image_url,
            "imageLink": image_link,
            "adFlag": ad_flag,
            "adult": adult,
            "pushAlarm": push_alarm,
            "header": header,
            "coupon": coupon,
            "item": item,
            "commerce": commerce,
            "list": list_,
            "head": head,
            "tail": tail,
            "video": video,
            "additionalContent": additional_content,
            "friendGroupKey": friend_group_key,
            "replaceSms": replace_sms,
            "smsSubject": sms_subject if replace_sms == "Y" else None,
            "smsContent": sms_content if replace_sms == "Y" else None,
            "rejectServiceId": reject_service_id,
            "webhooks": webhooks or [],
            "kakaoSenderKey": self._kakao_sender_key,
            "senderKey": self._sms_sender_key,
        }

        # A broadcast has no recipient list; sending an empty ``contacts`` would be
        # rejected as an invalid request, so the key is omitted entirely.
        if targeting != "F":
            body["contacts"] = contacts or []

        return self._http.post("brand-messages/send", body)

    def broadcast(self, **kwargs: Any) -> dict:
        """동보 발송 — 수신 동의한 전체 채널 친구 (``targeting="F"``).

        수신자 목록은 카카오 측에서 확장하므로 ``contacts`` 를 넘기지 않습니다.
        결과는 :meth:`campaigns` / :meth:`campaign` 으로 확인합니다.
        """
        kwargs.pop("contacts", None)
        kwargs["targeting"] = "F"

        return self.send(**kwargs)

    def campaigns(
        self,
        *,
        from_: str | None = None,
        to: str | None = None,
        count: int | None = None,
    ) -> dict:
        """브랜드메시지 캠페인 목록을 조회합니다.

        ``from_`` 은 파이썬 예약어 ``from`` 을 피하기 위한 이름이며,
        요청에는 ``from`` 으로 전송됩니다.
        """
        return self._http.get(
            "brand-messages",
            {"from": from_, "to": to, "count": count},
        )

    def campaign(self, campaign_id: str) -> dict:
        """브랜드메시지 캠페인 상세를 조회합니다.

        :param campaign_id: 발송 응답의 ``campaignId`` (UUID)
        """
        return self._http.get(f"brand-messages/{campaign_id}")
