from datetime import timedelta
from django.utils import timezone
from events.models import Event
from signals.models import Signal

def detect_silent_support_decay(company):
    now = timezone.now()
    last_7 = now - timedelta(days=7)
    prev_7 = now - timedelta(days=14)

    recent = Event.objects.filter(
        actor__company=company,
        event_type='ticket_reply',
        timestamp__gte=last_7
    ).count()

    previous = Event.objects.filter(
        actor__company=company,
        event_type='ticket_reply',
        timestamp__range=(prev_7, last_7)
    ).count()

    if previous == 0:
        return None

    drop_ratio = (previous - recent) / previous

    if drop_ratio >= 0.4:
        return Signal.objects.create(
            company=company,
            signal_type="Silent Support Decay",
            severity="high",
            explanation=(
                f"So‘nggi 7 kunda support javoblari {int(drop_ratio*100)}% ga kamaydi. "
                "Lekin tizimda xato yoki shikoyat yo‘q."
            ),
            predicted_impact=(
                "Agar davom etsa, 30–60 kun ichida user churn va renewal pasayishi kuzatiladi."
            )
        )
