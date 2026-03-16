# alerts/services.py

import logging
from django.db import transaction

from alerts.models import AlertHistory
from telegram_bot.sender import send_telegram_alert

logger = logging.getLogger(__name__)


def dispatch_telegram_alert(signal, recipient=None):
    """
    Sends telegram alert and writes AlertHistory.
    Never breaks API flow.
    Production-safe.
    """

    company = signal.company
    chat_id = company.telegram_chat_id

    # 🛑 Agar chat_id yo‘q bo‘lsa — yubormaymiz
    if not chat_id:
        logger.warning(
            f"No telegram_chat_id set for company {company.id}"
        )
        return False

    # 1️⃣ Alert message render
    message = (
        f"🚨 <b>CRITICAL ALERT</b>\n\n"
        f"Signal ID: {signal.id}\n"
        f"Company: {company.name}\n"
        f"Response Time: {signal.response_time_ms} ms\n"
        f"Error Rate: {signal.error_rate_percent}%\n"
        f"Downtime: {signal.downtime_minutes} min\n"
        f"Severity: {signal.severity.upper()}"
    )

    try:
        # 2️⃣ Telegram send (TO‘G‘RI)
        send_telegram_alert(chat_id, message)

        # 3️⃣ Success history
        with transaction.atomic():
            AlertHistory.objects.create(
                company=company,
                signal=signal,
                recipient=recipient,
                channel="telegram",
                status="sent",
                message=message,
            )

        logger.info(
            f"Telegram alert SENT for signal {signal.id}"
        )
        return True

    except Exception as e:
        # 4️⃣ Failure history
        with transaction.atomic():
            AlertHistory.objects.create(
                company=company,
                signal=signal,
                recipient=recipient,
                channel="telegram",
                status="failed",
                message=message,
                error_message=str(e),
            )

        logger.error(
            f"Telegram alert FAILED for signal {signal.id}: {str(e)}"
        )
        return False