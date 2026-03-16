import math


SEVERITY_WEIGHT = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 5,
}


def calculate_risk_score(severity, frequency=1, recency_factor=1):
    weight = SEVERITY_WEIGHT.get(severity, 1)

    score = weight * frequency * recency_factor

    # normalize
    return round(math.log1p(score) * 10, 2)