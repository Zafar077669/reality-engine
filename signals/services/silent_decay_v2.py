from datetime import timedelta
from django.utils import timezone
from events.models import Event
from signals.models import Signal

def avg_from_events(qs, key):
    values = []
    for e in qs:
        val = e.metadata.get(key)
        if isinstance(val, (int, float)):
            values.append(val)
    if not values:
        return None
    return sum(values) / len(values)

def detect_silent_support_decay_v2(company):
    now = timezone.now()
    cur = now - timedelta(days=7)
    prev = now - timedelta(days=14)

    def qs(start, end):
        return Event.objects.filter(
            actor__company=company,
            actor__role="support",
            event_type="ticket_reply",
            timestamp__range=(start, end)
        )

    cur_qs = qs(cur, now)
    prev_qs = qs(prev, cur)

    indicators = []

    # 1️⃣ Response volume drop
    if prev_qs.count() > 0:
        drop = (prev_qs.count() - cur_qs.count()) / prev_qs.count()
        if drop >= 0.4:
            indicators.append("response_volume_drop")

    # 2️⃣ Response time drift (MANUAL AVG)
    prev_rt = avg_from_events(prev_qs, "response_time_sec")
    cur_rt = avg_from_events(cur_qs, "response_time_sec")

    if prev_rt and cur_rt and cur_rt >= prev_rt * 1.3:
        indicators.append("response_time_drift")

    # 3️⃣ Message energy decay (MANUAL AVG)
    prev_len = avg_from_events(prev_qs, "message_length")
    cur_len = avg_from_events(cur_qs, "message_length")

    if prev_len and cur_len and cur_len <= prev_len * 0.65:
        indicators.append("message_energy_decay")

    # 4️⃣ Actor participation shrink
    prev_actors = prev_qs.values("actor").distinct().count()
    cur_actors = cur_qs.values("actor").distinct().count()

    if prev_actors > 0 and cur_actors <= prev_actors * 0.7:
        indicators.append("actor_participation_shrink")

    score = len(indicators)

    if score < 2:
        return None

    severity = (
        "low" if score == 2 else
        "medium" if score == 3 else
        "high"
    )

    return Signal.objects.create(
        company=company,
        signal_type="Silent Support Decay",
        severity=severity,
        explanation=(
            f"Support faoliyatida {score} ta mustaqil og‘ish aniqlandi: "
            + ", ".join(indicators)
        ),
        predicted_impact=(
            "Agar bu holat davom etsa, 30–60 kun ichida "
            "user churn, NPS pasayishi va support burnout kuchayishi mumkin."
        )
    )
