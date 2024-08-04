from email.message import Message


def get_payload(msg: Message, content_type: str = "text/html") -> str:
    payload: str = ""

    for p in msg.walk():
        if p.get_content_type() == content_type:
            payload = p.get_payload(decode=True).decode("utf-8")
            break

    return payload
