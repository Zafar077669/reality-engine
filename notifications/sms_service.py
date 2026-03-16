from twilio.rest import Client


def send_sms_alert(incident, config):

    client = Client(
        config["account_sid"],
        config["auth_token"]
    )

    client.messages.create(
        body=f"Incident #{incident.id} detected",
        from_=config["from_number"],
        to=config["to_number"]
    )