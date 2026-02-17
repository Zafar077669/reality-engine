from .models import AuditLog


def create_audit_log(
    *,
    user=None,
    company=None,
    action,
    object_type,
    object_id=None,
    metadata=None,
    request=None,
):
    AuditLog.objects.create(
        user=user,
        company=company,
        action=action,
        object_type=object_type,
        object_id=object_id,
        metadata=metadata or {},
        ip_address=getattr(request, "META", {}).get("REMOTE_ADDR"),
    )
