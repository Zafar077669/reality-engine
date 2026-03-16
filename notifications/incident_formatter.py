from django.utils.timezone import localtime


def format_incident_message(incident):
    company_name = incident.company.name if incident.company else "N/A"
    started = localtime(incident.opened_at).strftime("%Y-%m-%d %H:%M:%S")

    return (
        "🚨 *INCIDENT OPENED*\n\n"
        f"🆔 ID: `{incident.id}`\n"
        f"🏢 Company: *{company_name}*\n"
        f"📡 Agent: `{incident.infra_agent}`\n"
        f"⏱ Opened at: `{started}`\n"
        f"📌 Status: *{incident.status.upper()}*"
    )