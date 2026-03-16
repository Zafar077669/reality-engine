import logging
from django.db import transaction

from alerts.models import AlertHistory
from notifications.telegram_client import TelegramClient
from notifications.incident_formatter import format_incident_message
from notifications.buttons import incident_buttons

logger = logging.getLogger(__name__)


def dispatch_incident_created(incident):

    # Faqat OPEN incidentlar
    if incident.status != "open":
        return

    # Dedup
    if incident.telegram_notified:
        logger.info(f"Telegram already sent for incident {incident.id}")
        return

    company = incident.company
    chat_id = getattr(company, "telegram_chat_id", None)

    if not chat_id:
        logger.warning(f"No telegram_chat_id for company {company.id}")
        return

    message = format_incident_message(incident)
    buttons = incident_buttons(incident.id)

    client = TelegramClient()

    try:
        # 1️⃣ Telegram yuborish
        client.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=buttons,
        )

    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return  # Telegram yuborilmasa DB ham yozmaymiz

    # 2️⃣ DB yozish (alohida blok)
    try:
        with transaction.atomic():

            AlertHistory.objects.create(
                company=company,
                incident=incident,
                channel="telegram",
                status="sent",
                message=message,
            )

            incident.telegram_notified = True
            incident.save(update_fields=["telegram_notified"])

    except Exception as e:
        logger.error(f"AlertHistory save failed: {e}")
        raise  # Bu safar silent yutmaydi