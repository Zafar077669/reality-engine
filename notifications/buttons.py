def incident_buttons(incident_id):
    return {
        "inline_keyboard": [
            [
                {
                    "text": "✅ ACK",
                    "callback_data": f"ack:{incident_id}"
                },
                {
                    "text": "🟢 RESOLVE",
                    "callback_data": f"resolve:{incident_id}"
                },
            ]
        ]
    }