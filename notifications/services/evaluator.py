from notifications.services.service import NotificationService


class SignalEvaluator:

    def evaluate(self, signal):
        """
        Severity hisoblaydi va notify qiladi
        """

        # 🔥 1. Severity hisoblash
        calculated_severity = self._calculate_severity(signal)

        signal.severity = calculated_severity
        signal.save()

        # 🔥 2. Notify (faqat high/critical ichida)
        NotificationService().notify(signal)

        return signal

    def _calculate_severity(self, signal):
        if signal.response_time_ms > 2000:
            return "critical"
        elif signal.response_time_ms > 1000:
            return "high"
        elif signal.response_time_ms > 500:
            return "medium"
        return "low"