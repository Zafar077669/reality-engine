import requests
from django.conf import settings

class TelegramClient:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{settings.TELEGRAM['TOKEN']}"

    def send_message(self, chat_id, text, reply_markup=None):
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup

        requests.post(
            f"{self.base_url}/sendMessage",
            json=payload,
            timeout=5
        )