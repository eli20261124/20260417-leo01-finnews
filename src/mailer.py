from __future__ import annotations

import smtplib
import ssl
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


@dataclass
class EmailSettings:
    enabled: bool
    recipient: str | None
    sender: str | None
    app_password: str | None


def send_report_email(settings: EmailSettings, html: str, output_path: Path, generated_at: datetime) -> bool:
    if not settings.enabled:
        return False
    if not settings.recipient or not settings.sender or not settings.app_password:
        print("EMAIL_ENABLED=true but EMAIL_TO, EMAIL_FROM, or EMAIL_APP_PASSWORD is missing; skipping email send.")
        return False

    message = EmailMessage()
    message["Subject"] = f"FinNews Daily Brief - {generated_at.strftime('%Y-%m-%d')}"
    message["From"] = settings.sender
    message["To"] = settings.recipient
    message.set_content("Your email client does not support HTML. Please open the attached FinNews report.")
    message.add_alternative(html, subtype="html")

    message.add_attachment(
        output_path.read_bytes(),
        maintype="text",
        subtype="html",
        filename=output_path.name,
    )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(settings.sender, settings.app_password)
        server.send_message(message)
    return True