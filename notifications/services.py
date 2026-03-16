from notifications.telegram_client import TelegramClient
from notifications.incident_formatter import format_incident_message
from notifications.buttons import incident_buttons

def notify_incident_created(incident):
    if incident.severity != "CRITICAL":
        return

    if incident.telegram_notified:
        return  # 🔒 dedup

    client = TelegramClient()

    client.send_message(
        chat_id=incident.company.telegram_chat_id,
        text=format_incident_message(incident),
        reply_markup=incident_buttons(incident.id)
    )

    incident.telegram_notified = True
    incident.save(update_fields=["telegram_notified"])