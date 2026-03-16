import requests


def send_telegram_alert(incident, config):

    token = config["bot_token"]
    chat_id = config["chat_id"]

    message = f"""
🚨 REALITY ENGINE INCIDENT

ID: {incident.id}
Company: {incident.company.name}
Status: {incident.status}
"""

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    requests.post(url, json={
        "chat_id": chat_id,
        "text": message
    })