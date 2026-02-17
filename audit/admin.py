from django.contrib import admin

# Register your models here.
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "action",
        "user",
        "company",
        "object_type",
        "object_id",
    )
    list_filter = ("action", "company")
    search_fields = ("user__username", "object_type")
    readonly_fields = (
        "user",
        "company",
        "action",
        "object_type",
        "object_id",
        "metadata",
        "ip_address",
        "created_at",
    )
