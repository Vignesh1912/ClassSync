"""
email.py — Sends emails via Resend REST API (https://resend.com).
Set RESEND_API_KEY in .env.  Falls back silently if not configured.
"""
import logging
import requests

logger = logging.getLogger(__name__)

RESEND_SEND_URL = 'https://api.resend.com/emails'
FROM_ADDRESS = 'ClassSync <onboarding@resend.dev>'  # default sandbox sender


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email via Resend. Returns True on success."""
    try:
        from flask import current_app
        api_key = current_app.config.get('RESEND_API_KEY', '')
        if not api_key:
            logger.warning("RESEND_API_KEY not configured — skipping email to %s", to)
            return False

        resp = requests.post(
            RESEND_SEND_URL,
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'from': FROM_ADDRESS,
                'to': [to],
                'subject': subject,
                'text': body,
            },
            timeout=10,
        )

        if resp.ok:
            logger.info("Email sent to %s | subject: %s", to, subject)
            return True
        else:
            logger.warning("Resend error (%s): %s", resp.status_code, resp.text)
            return False

    except Exception as exc:
        logger.warning("Failed to send email to %s: %s", to, exc)
        return False


def send_reminder_email(student_email: str, student_name: str,
                        assignment_title: str, deadline,
                        days_remaining: int, classroom_link=None) -> bool:
    """Send an assignment deadline reminder email."""
    if days_remaining == 0:
        subject_line = f"[ClassSync] Due TODAY: {assignment_title}"
        body_intro   = "This assignment is due today!"
    else:
        subject_line = f"[ClassSync] Reminder: {assignment_title} due in {days_remaining} day(s)"
        body_intro   = f"This assignment is due in {days_remaining} day(s)."

    deadline_str = deadline.strftime('%A, %d %b %Y at %H:%M')
    link_text    = f"\nGoogle Classroom: {classroom_link}" if classroom_link else ''

    body = (
        f"Hi {student_name},\n\n"
        f"{body_intro}\n\n"
        f"Assignment : {assignment_title}\n"
        f"Deadline   : {deadline_str}"
        f"{link_text}\n\n"
        f"Log in to ClassSync to mark it as submitted once done.\n\n"
        f"— ClassSync"
    )
    return send_email(student_email, subject_line, body)
