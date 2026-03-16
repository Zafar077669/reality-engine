from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class NotificationPayload:
    company_id: int
    signal_id: int
    severity: str
    message: str
    meta: Dict[str, Any]