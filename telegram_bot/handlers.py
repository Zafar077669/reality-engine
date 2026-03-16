from incidents.models import Incident

def handle_callback(data, user):
    action, incident_id = data.split(":")
    incident = Incident.objects.get(id=incident_id)

    if action == "ack":
        incident.status = "ACKNOWLEDGED"
        incident.ack_by = user.username
        incident.save()

    elif action == "resolve":
        incident.resolve()