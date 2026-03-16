class ConsoleNotifier:
    def send(self, payload):
        print("🔔 NOTIFICATION")
        print(f"Company: {payload.company_id}")
        print(f"Signal: {payload.signal_id}")
        print(f"Severity: {payload.severity}")
        print(f"Message: {payload.message}")