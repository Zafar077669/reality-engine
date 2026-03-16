from .severity import calculate_severity
from .risk_engine import calculate_risk_score


def evaluate_signal(signal):
    company = signal.company

    severity = calculate_severity(company, signal)
    signal.severity = severity

    risk_score = calculate_risk_score(severity)
    signal.risk_score = risk_score

    signal.save()

    return signal