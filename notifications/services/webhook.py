import logging

logger = logging.getLogger(__name__)


class WebhookNotifier:
    def send(self, payload):
        # Real HTTP YO‘Q (keyin qo‘shamiz)
        data = {
            "text": f"🚨 {payload.severity.upper()} ALERT",
            "attachments": [
                {
                    "fields": [
                        {"title": "Company", "value": payload.company_id},
                        {"title": "Signal", "value": payload.signal_id},
                        {"title": "Message", "value": payload.message},
                    ]
                }
            ],
        }

        logger.info("[WEBHOOK] %s", data)