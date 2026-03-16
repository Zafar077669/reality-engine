import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    def send(self, payload):
        # HOZIRCHA: console mock (serverga xalaqit bermaydi)
        logger.info(
            "[EMAIL] company=%s signal=%s severity=%s message=%s",
            payload.company_id,
            payload.signal_id,
            payload.severity,
            payload.message,
        )