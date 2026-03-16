import requests
from django.conf import settings


def send_telegram_alert(chat_id: int, message: str):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set")

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()

    return response.json()