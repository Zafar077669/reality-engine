import requests


def send_slack_alert(incident, config):

    webhook_url = config["webhook"]

    payload = {
        "text": f"""
🚨 Reality Engine Incident

ID: {incident.id}
Company: {incident.company.name}
Status: {incident.status}
"""
    }

    requests.post(webhook_url, json=payload)