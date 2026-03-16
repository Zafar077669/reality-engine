import logging
import os

from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail

import requests

from alerts.models import AlertRule, AlertHistory
from telegram_bot.sender import send_telegram_alert

logger = logging.getLogger(__name__)


def dispatch_alert(signal):
    """
    Enterprise Signal Alert Dispatcher

    Workflow:
        Signal -> AlertRule filter -> Channel dispatch -> AlertHistory log
    """

    if not signal:
        logger.warning("[Signal Alert] dispatch_alert called with empty signal")
        return

    try:
        rules = AlertRule.objects.filter(
            company=signal.company,
            severity=signal.severity,
            is_active=True,
        )
    except Exception as e:
        logger.error(f"[Signal Alert] Rule query failed: {str(e)}")
        return

    if not rules.exists():
        logger.info(
            f"[Signal Alert] No rules matched for signal {signal.id}"
        )
        return

    message = _build_signal_message(signal)

    for rule in rules:

        if rule.send_telegram:
            _dispatch_telegram(signal, message)

        if getattr(rule, "send_email", False):
            _dispatch_email(signal, message)

        if getattr(rule, "send_slack", False):
            _dispatch_slack(signal, message)

        if getattr(rule, "send_sms", False):
            _dispatch_sms(signal, message)


# ============================================================
# TELEGRAM DISPATCH
# ============================================================

def _dispatch_telegram(signal, message):

    company = signal.company

    chat_id = getattr(company, "telegram_chat_id", None)

    if not chat_id:
        chat_id = os.getenv("TELEGRAM_DEFAULT_CHAT_ID")

    if not chat_id:
        chat_id = getattr(settings, "TELEGRAM_CHAT_ID", None)

    if not chat_id:
        logger.warning(
            f"[Signal Alert] No Telegram chat configured for company {company.id}"
        )
        return

    try:

        send_telegram_alert(chat_id, message)

        with transaction.atomic():
            AlertHistory.objects.create(
                company=company,
                signal=signal,
                channel="telegram",
                status="sent",
                message=message,
            )

        logger.info(
            f"[Signal Alert] Telegram SENT for signal {signal.id}"
        )

    except Exception as e:

        _log_failure(signal, message, "telegram", str(e))


# ============================================================
# EMAIL DISPATCH
# ============================================================

def _dispatch_email(signal, message):

    company = signal.company
    email = getattr(company, "alert_email", None)

    if not email:
        logger.warning(f"[Alert Email] No email configured for company {company.id}")
        return

    try:

        send_mail(
            subject=f"[Reality Engine] Alert #{signal.id}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        AlertHistory.objects.create(
            company=company,
            signal=signal,
            channel="email",
            status="sent",
            message=message,
        )

        logger.info(f"[Alert Email] SENT for signal {signal.id}")

    except Exception as e:

        _log_failure(signal, message, "email", str(e))


# ============================================================
# SLACK DISPATCH
# ============================================================

def _dispatch_slack(signal, message):

    company = signal.company
    webhook = getattr(company, "slack_webhook_url", None)

    if not webhook:
        return

    payload = {
        "text": message
    }

    try:

        requests.post(webhook, json=payload, timeout=5)

        AlertHistory.objects.create(
            company=company,
            signal=signal,
            channel="slack",
            status="sent",
            message=message,
        )

        logger.info(f"[Alert Slack] SENT for signal {signal.id}")

    except Exception as e:

        _log_failure(signal, message, "slack", str(e))


# ============================================================
# SMS DISPATCH (simple gateway)
# ============================================================

def _dispatch_sms(signal, message):

    company = signal.company
    phone = getattr(company, "alert_phone", None)

    if not phone:
        return

    sms_api = getattr(settings, "SMS_GATEWAY_URL", None)

    if not sms_api:
        logger.warning("[SMS] SMS_GATEWAY_URL not configured")
        return

    try:

        requests.post(
            sms_api,
            json={
                "phone": phone,
                "message": message
            },
            timeout=5
        )

        AlertHistory.objects.create(
            company=company,
            signal=signal,
            channel="sms",
            status="sent",
            message=message,
        )

        logger.info(f"[Alert SMS] SENT for signal {signal.id}")

    except Exception as e:

        _log_failure(signal, message, "sms", str(e))


# ============================================================
# FAILURE LOGGER
# ============================================================

def _log_failure(signal, message, channel, error):

    try:

        AlertHistory.objects.create(
            company=signal.company,
            signal=signal,
            channel=channel,
            status="failed",
            message=message,
            error_message=error,
        )

    except Exception:
        logger.error("[Signal Alert] Failed writing AlertHistory")

    logger.error(
        f"[Signal Alert] {channel.upper()} FAILED for signal {signal.id}: {error}"
    )


# ============================================================
# MESSAGE BUILDER
# ============================================================

def _build_signal_message(signal):

    metric_value = getattr(signal, "metric_value", None)
    if metric_value is None:
        metric_value = getattr(signal, "current_value", "N/A")

    metric = getattr(signal, "metric", "unknown")
    source = getattr(signal, "source", "unknown")
    severity = getattr(signal, "severity", "unknown")

    company_name = getattr(signal.company, "name", "Unknown Company")

    return (
        "🚨 REALITY ENGINE ALERT\n\n"
        f"🆔 Signal ID: {signal.id}\n"
        f"🏢 Company: {company_name}\n"
        f"📡 Source: {source}\n"
        f"📊 Metric: {metric}\n"
        f"🚦 Severity: {severity.upper()}\n"
        f"📈 Value: {metric_value}"
    )