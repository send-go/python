# 로컬 모의 서버 전용.
import os
from sendgo import Sendgo, EmailService, SendgoError
url=os.environ['SENDGO_TEST_URL']
email=Sendgo(access_key='ak',secret_key='sk',api_version='v2',base_url=url).email
basic=EmailService.with_credentials('credential','password',url)
body={'subject':'한글','enabled':False,'optional':None,'idempotency_key':'fixed-key','attachments':[{'name':'a.txt','type':'text/plain','content':'aGk='}]}
query={'search':'한글 +&','page':'2'}
def check(value,name,verb):
    if name=='rawMessage': assert value==bytes([69,77,76,13,10,0,255])
    elif verb=='DELETE': assert value is None
    elif name=='domains': assert value[0]['marker']=='한글'
    else: assert value['marker']=='한글'
check(email.account(query),'account','GET')
check(email.request_access(body),'requestAccess','POST')
check(email.create_credential(body),'createCredential','POST')
check(email.credentials(query),'credentials','GET')
check(email.revoke_credential("id 한글+"),'revokeCredential','DELETE')
check(email.domains(query),'domains','GET')
check(email.register_domain(body),'registerDomain','POST')
check(email.verify_domain("id 한글+", body),'verifyDomain','POST')
check(email.senders(query),'senders','GET')
check(email.request_sender(body),'requestSender','POST')
check(email.verify_sender("id 한글+", body),'verifySender','POST')
check(email.request_recipient_verification(body),'requestRecipientVerification','POST')
check(email.check_recipients(body),'checkRecipients','POST')
check(email.address_book(query),'addressBook','GET')
check(email.sender_profiles(query),'senderProfiles','GET')
check(email.create_sender_profile(body),'createSenderProfile','POST')
check(email.update_sender_profile("id 한글+", body),'updateSenderProfile','PATCH')
check(email.delete_sender_profile("id 한글+"),'deleteSenderProfile','DELETE')
check(email.import_address_book(body),'importAddressBook','POST')
check(email.update_address_book_preferences(body),'updateAddressBookPreferences','POST')
check(email.send(body),'send','POST')
check(email.quote(body),'quote','POST')
check(email.messages(query),'messages','GET')
check(email.message("id 한글+", query),'message','GET')
check(email.cancel_message("id 한글+", body),'cancelMessage','POST')
check(email.inboxes(query),'inboxes','GET')
check(email.create_inbox(body),'createInbox','POST')
check(email.update_inbox("id 한글+", body),'updateInbox','PATCH')
check(email.inbox_messages("id 한글+", query),'inboxMessages','GET')
check(email.inbox_message("id 한글+", "id 한글+", query),'inboxMessage','GET')
check(email.raw_message("id 한글+", "id 한글+", query),'rawMessage','GET')
check(email.delete_inbox_message("id 한글+", "id 한글+"),'deleteInboxMessage','DELETE')
check(email.templates(query),'templates','GET')
check(email.template("id 한글+", query),'template','GET')
check(email.create_template(body),'createTemplate','POST')
check(email.update_template("id 한글+", body),'updateTemplate','PATCH')
check(email.delete_template("id 한글+"),'deleteTemplate','DELETE')
check(email.contacts(query),'contacts','GET')
check(email.save_contact(body),'saveContact','POST')
check(email.import_contacts(body),'importContacts','POST')
check(email.unsubscribe_contact("id 한글+", body),'unsubscribeContact','POST')
check(email.campaigns(query),'campaigns','GET')
check(email.create_campaign(body),'createCampaign','POST')
check(email.campaign("id 한글+", query),'campaign','GET')
check(email.quote_campaign("id 한글+", body),'quoteCampaign','POST')
check(email.send_campaign("id 한글+", body),'sendCampaign','POST')
check(email.cancel_campaign("id 한글+", body),'cancelCampaign','POST')
check(basic.domains(query),'domains','GET')
check(basic.register_domain(body),'registerDomain','POST')
check(basic.verify_domain("id 한글+", body),'verifyDomain','POST')
check(basic.send(body),'send','POST')
check(basic.quote(body),'quote','POST')
check(basic.messages(query),'messages','GET')
check(basic.message("id 한글+", query),'message','GET')
check(basic.cancel_message("id 한글+", body),'cancelMessage','POST')
check(basic.auth(query),'auth','GET')
check(email.messages({'mode':'refresh'}),'messages','GET')
try:
    email.messages({'mode':'403'})
    raise AssertionError('missing error')
except SendgoError as e:
    assert e.status_code==403
try:
    email.messages({'mode':'422'})
    raise AssertionError('missing error')
except SendgoError as e:
    assert e.status_code==422
try:
    email.messages({'mode':'429'})
    raise AssertionError('missing error')
except SendgoError as e:
    assert e.status_code==429
try:
    email.messages({'mode':'500'})
    raise AssertionError('missing error')
except SendgoError as e:
    assert e.status_code==500
try:
    basic.messages({'mode':'401'})
    raise AssertionError('missing error')
except SendgoError as e:
    assert e.status_code==401
Sendgo(access_key='ak',secret_key='sk',api_version='v2',base_url=url).brand_message.send(friend_template_uuid='template',targeting='O',contacts=[{'contact':'01000000000'}])
print('PASS email')
