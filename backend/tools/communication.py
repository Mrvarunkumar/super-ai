"""
Communication tools: local notifications now, email/SMS as a configurable stub.
Fill in SMTP credentials via environment variables before using send_email.
"""
import os
import platform
import subprocess
import smtplib
from email.mime.text import MIMEText

OS_NAME = platform.system()


def send_notification(title: str, message: str) -> dict:
    try:
        if OS_NAME == "Windows":
            # requires: pip install win10toast
            from win10toast import ToastNotifier
            ToastNotifier().show_toast(title, message, duration=5)
        elif OS_NAME == "Darwin":
            subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'])
        else:
            subprocess.run(["notify-send", title, message])
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e), "note": "Platform notification lib may need installing."}


def send_email(to: str, subject: str, body: str) -> dict:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    if not all([smtp_host, smtp_user, smtp_pass]):
        return {"success": False, "error": "SMTP_HOST/SMTP_USER/SMTP_PASS not configured in environment."}
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to
        with smtplib.SMTP_SSL(smtp_host, 465) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to], msg.as_string())
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


TOOL_SCHEMAS = [
    {"name": "send_notification", "description": "Show a desktop notification.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "message": {"type": "string"}}, "required": ["title", "message"]}},
    {"name": "send_email", "description": "Send an email via configured SMTP.", "input_schema": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["to", "subject", "body"]}},
]
