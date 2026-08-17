import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger("intellimoney")

RESEND_API_URL = "https://api.resend.com/emails"


async def send_email(
    to: str,
    subject: str,
    html: str,
    text: str | None = None,
) -> bool:
    settings = get_settings()
    api_key = settings.resend_api_key
    if not api_key:
        logger.warning("Resend API key not configured; skipping email to %s (subject=%s)", to, subject)
        return False

    payload = {
        "from": settings.resend_from_email,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if text:
        payload["text"] = text

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                RESEND_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if response.status_code >= 200 and response.status_code < 300:
            logger.info("email_sent to=%s subject=%s", to, subject)
            return True
        logger.error("email_failed to=%s status=%s body=%s", to, response.status_code, response.text[:300])
        return False
    except Exception as exc:
        logger.error("email_error to=%s error=%s", to, exc)
        return False


def render_otp_email(otp_code: str, name: str) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: auto; padding: 24px; border: 1px solid #e5e7eb; border-radius: 12px;">
      <h2 style="color: #065f46; margin-bottom: 8px;">IntelliMoney</h2>
      <p>Hi {name},</p>
      <p>Your verification code is:</p>
      <div style="font-size: 32px; font-weight: 700; letter-spacing: 8px; color: #059669; background: #ecfdf5; padding: 12px; text-align: center; border-radius: 8px;">
        {otp_code}
      </div>
      <p>This code is valid for 10 minutes. If you didn't request this, you can ignore this email.</p>
      <p style="color: #6b7280; font-size: 12px; margin-top: 24px;">IntelliMoney - AI-powered financial health</p>
    </div>
    """
