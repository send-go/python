"""모의 서버 전용 폴더 계약 검증. 실제 API는 호출하지 않습니다."""
import os
from sendgo import Sendgo
from sendgo.exceptions import SendgoError
c = Sendgo(access_key="test-access", secret_key="test-secret", api_version="v2", base_url=os.environ["SENDGO_TEST_URL"])
f = "11111111-1111-4111-8111-111111111111"
key = "채널 /?"
c.template_folders.list()
c.template_folders.list(template_type="brand", kakao_sender_key=key)
c.template_folders.create(name="주문")
c.template_folders.create(name="하위", parent_uuid=f)
for kind in ["notice", "brand"]:
    c.template_folders.assign(template_type=kind, kakao_sender_key=key, template_codes=["코드 1", "code/2"], folder_uuid=f)
    c.template_folders.assign(template_type=kind, kakao_sender_key=key, template_codes=["코드 1"], folder_uuid=None)
c.notice_templates.list(folder_uuid="none")
c.brand_templates.list(folder_uuid=f)
c.notice_templates.create(kakao_sender_key=key, template_name="테스트", template_content="본문", template_message_type="BA", template_emphasize_type="NONE", category_code="001001", message_purpose="order_delivery", legal_basis="transaction", benefit_origin="none", expiry_type="none", folder_uuid=f)
c.brand_templates.create(kakao_sender_key=key, template_name="테스트", template_type="FT", folder_uuid=f)
for kind, status, code in [("forbidden",403,"ACCESS_KEY_NOT_APPROVED"),("invalid",422,"VALIDATION_FAILED"),("missing",404,"TEMPLATE_FOLDER_NOT_FOUND")]:
    try:
        c.template_folders.list(template_type=kind)
        raise AssertionError("오류가 발생하지 않음")
    except SendgoError as e:
        assert (e.status_code, e.error_code) == (status, code)
