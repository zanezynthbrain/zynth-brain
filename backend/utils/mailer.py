"""Email delivery channel — updates reach the MD's inbox, not just Telegram.

Uses plain SMTP (Gmail/Workspace App Password). Configure:
  SMTP_USER      = zane@zynth.asia
  SMTP_PASSWORD  = 16-char Google App Password (myaccount.google.com/apppasswords)
  ZYNTH_EMAIL_TO = recipient (defaults to SMTP_USER)

Unconfigured → every send is a silent no-op returning False, so Telegram
remains the primary channel and nothing breaks.
"""

from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage
from pathlib import Path

from config import get_settings
from utils.logging_config import get_logger

logger = get_logger("mailer")


def has_email() -> bool:
    s = get_settings()
    return bool(s.smtp_user and s.smtp_password)


def _send_sync(subject: str, body: str, attachments: list[Path]) -> None:
    s = get_settings()
    msg = EmailMessage()
    msg["From"] = s.smtp_user
    msg["To"] = s.email_to or s.smtp_user
    msg["Subject"] = subject
    msg.set_content(body)

    for path in attachments:
        data = Path(path).read_bytes()
        if str(path).endswith(".docx"):
            maintype, subtype = (
                "application",
                "vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        elif str(path).endswith(".pdf"):
            maintype, subtype = "application", "pdf"
        else:
            maintype, subtype = "application", "octet-stream"
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=Path(path).name)

    with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=30) as server:
        server.starttls()
        server.login(s.smtp_user, s.smtp_password)
        server.send_message(msg)


async def send_email(subject: str, body: str, attachments: list[Path] | None = None) -> bool:
    """Send an email; returns True on success, False if unconfigured/failed."""
    if not has_email():
        return False
    try:
        await asyncio.to_thread(_send_sync, subject, body, attachments or [])
        logger.info("Email sent: %s", subject)
        return True
    except Exception as exc:
        logger.warning("Email send failed: %s", exc)
        return False
