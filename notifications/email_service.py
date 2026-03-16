from django.core.mail import send_mail
from django.conf import settings


def send_email_alert(incident, config):

    subject = f"[Reality Engine] Incident #{incident.id}"

    message = f"""
Incident ID: {incident.id}
Company: {incident.company.name}
Status: {incident.status}

Please investigate immediately.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [config["email"]],
        fail_silently=False,
    )