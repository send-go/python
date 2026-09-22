import os
from sendgo import AccountClient, SendgoError
url = os.environ['SENDGO_TEST_URL'] + '/'
try:
    AccountClient(agent_token='')
    raise AssertionError('빈 토큰 허용')
except ValueError:
    pass
c = AccountClient(agent_token='test-agent', base_url=url)
assert c.me()["message"] == "Success"
assert c.organizations()["message"] == "Success"
assert c.select_organization(None)["message"] == "Success"
assert c.select_organization("team-id")["message"] == "Success"
assert c.api_keys()["message"] == "Success"
assert c.create_api_key({"name": "한글 이름", "ipAddresses": [{"ip": "192.0.2.1", "description": "서버"}]})["message"] == "Success"
assert c.api_key("key/id ?")["message"] == "Success"
assert c.update_api_key("key/id ?", "새 이름")["message"] == "Success"
assert c.delete_api_key("key/id ?")["message"] == "Success"
assert c.issue_token("key/id ?")["message"] == "Success"
assert c.allowed_ips("key/id ?")["message"] == "Success"
assert c.add_allowed_ip("key/id ?", {"ip": "192.0.2.1", "description": "서버"})["message"] == "Success"
assert c.delete_allowed_ip("key/id ?", "ip/id ?")["message"] == "Success"
for token, status, code in [('expired', 401, 'AGENT_TOKEN_EXPIRED'), ('forbidden', 403, 'AGENT_ABILITY_MISSING')]:
    try:
        AccountClient(agent_token=token, base_url=url).me()
        raise AssertionError('오류가 발생하지 않음')
    except SendgoError as error:
        assert error.status_code == status and error.error_code == code
