from infra.models import InfraMetricHistory
from incidents.models import Incident


def calculate_agent_health(agent):
    """
    Calculates infrastructure health score (0-100)
    """

    cpu = InfraMetricHistory.objects.filter(
        infra_agent=agent,
        metric="cpu"
    ).order_by("-created_at").first()

    ram = InfraMetricHistory.objects.filter(
        infra_agent=agent,
        metric="ram"
    ).order_by("-created_at").first()

    disk = InfraMetricHistory.objects.filter(
        infra_agent=agent,
        metric="disk"
    ).order_by("-created_at").first()

    cpu_val = cpu.value if cpu else 0
    ram_val = ram.value if ram else 0
    disk_val = disk.value if disk else 0

    active_incidents = Incident.objects.filter(
        infra_agent=agent,
        status__in=["open", "investigating"]
    ).count()

    health = (
        100
        - cpu_val * 0.2
        - ram_val * 0.4
        - disk_val * 0.2
        - active_incidents * 10
    )

    return max(0, min(100, int(health)))