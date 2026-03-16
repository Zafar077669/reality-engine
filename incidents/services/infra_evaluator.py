from incidents.services.incident_manager import attach_signal_to_incident

signal = Signal.objects.create(...)
attach_signal_to_incident(signal)