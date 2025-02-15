from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from settings import SMTP_PASSWORD, SMTP_PORT, SMTP_SERVER, SMTP_USERNAME

"""Отправка кода подтверждения на указанный email"""


async def send_verification_code(email: str, code: str) -> dict:
    message = MIMEMultipart()
    message["From"] = SMTP_USERNAME
    message["To"] = email
    message["Subject"] = "Код подтверждения"

    text = f"Ваш код подтверждения: {code}"
    message.attach(MIMEText(text, "plain"))

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            use_tls=True,
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
