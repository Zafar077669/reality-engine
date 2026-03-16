def calculate_severity(company, signal):
    if signal.downtime_minutes > company.sla_downtime_minutes:
        return "critical"

    if signal.response_time_ms > company.sla_response_time_ms:
        return "high"

    if signal.error_rate_percent > company.sla_error_rate_percent:
        return "medium"

    return "low"