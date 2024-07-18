from typing import Any

from pydantic import EmailStr

from fastapi_mail import FastMail, MessageSchema, MessageType
from jinja2 import Template, TemplateNotFound

from miolingo import settings

fast_mail: FastMail = FastMail(settings.SMTP_CONFIG)


async def send_mail_with_template(
    subject: str,
    recipients: list[EmailStr],
    template_name: str,
    template_body: dict[str, Any],
    **kwargs: Any,
) -> None:
    # First prepare the alternative text to HTML
    try:
        template: Template = await fast_mail.get_mail_template(
            env_path=fast_mail.config.template_engine(),
            template_name=template_name.replace(".html", ".txt"),
        )
    except TemplateNotFound:
        alternative_body = None
    else:
        alternative_body = template.render(**template_body)

    # Then build the message schema.
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=template_body,
        alternative_body=alternative_body,
        subtype=MessageType.html,
        **kwargs,
    )

    # Finally send the HTML email with text alternative.
    await fast_mail.send_message(message, template_name=template_name)