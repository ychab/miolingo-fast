from email.message import Message

from fastapi_mail import FastMail

from miolingo.conf.settings import BASE_DIR, Settings
from miolingo.utils import mails as mail_utils
from miolingo.utils.mails import send_mail_with_template
from tests.utils.mails import get_payload

test_settings = Settings(MAIL_TEMPLATE_FOLDER=BASE_DIR / "tests" / "units" / "templates" / "mails")
fast_mail = FastMail(test_settings.SMTP_CONFIG)


async def test_mail_alternative_none(monkeypatch):
    monkeypatch.setattr(mail_utils, "fast_mail", fast_mail)

    with fast_mail.record_messages() as outbox:
        await send_mail_with_template(
            subject="Test",
            recipients=["test@example.com"],
            template_name="dummy.html",
            template_body={
                "name": "foo",
            },
        )

    assert len(outbox) == 1
    msg: Message = outbox[0]
    assert msg["Subject"] == "Test"
    assert "Dear Dummy foo" in get_payload(msg)
    assert not get_payload(msg, "text/plain")


async def test_mail_alternative(monkeypatch):
    monkeypatch.setattr(mail_utils, "fast_mail", fast_mail)

    with fast_mail.record_messages() as outbox:
        await send_mail_with_template(
            subject="Test",
            recipients=["test@example.com"],
            template_name="dummy_alt.html",
            template_body={
                "name": "foo",
            },
        )

    assert len(outbox) == 1
    msg: Message = outbox[0]
    assert msg["Subject"] == "Test"
    assert "Test alt for foo" in get_payload(msg)
    assert "Test alt for foo" == get_payload(msg, "text/plain")
