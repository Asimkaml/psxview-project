"""Simple OTP email sender.

In development, when SMTP_HOST is empty, we just log the OTP instead of
sending a real email. This keeps the flow testable without credentials.
"""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from config import config

log = logging.getLogger("psxviewai.emailer")


def send_otp_email(to_email: str, code: str) -> None:
    subject = "Your PSXviewAI login code"
    body = f"Your one-time code is: {code}\n\nIt expires in 10 minutes."

    if not config.smtp_host:
        # Development / test mode: just log the code.
        log.info("OTP for %s: %s", to_email, code)
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.smtp_from or (config.smtp_user or "no-reply@localhost")
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
        server.starttls()
        if config.smtp_user and config.smtp_password:
            server.login(config.smtp_user, config.smtp_password)
        server.send_message(msg)
