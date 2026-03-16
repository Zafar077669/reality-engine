from django.contrib import admin

from alerts.models import AlertHistory, AlertRule


# ============================================================
# ALERT HISTORY ADMIN
# ============================================================

@admin.register(AlertHistory)
class AlertHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "company",
        "signal_id",
        "channel",
        "status",
        "recipient",
        "created_at",
        "acked_at",
    )

    list_filter = (
        "status",
        "channel",
        "company",
        "created_at",
    )

    search_fields = (
        "signal__id",
        "recipient__username",
        "message",
        "error_message",
    )

    readonly_fields = (
        "company",
        "signal",
        "incident",
        "recipient",
        "channel",
        "message",
        "error_message",
        "created_at",
        "acked_at",
        "status",
        "acknowledged_by",
    )

    ordering = ("-created_at",)

    list_per_page = 50

    def signal_id(self, obj):
        if obj.signal:
            return obj.signal.id
        return None

    signal_id.short_description = "Signal ID"


# ============================================================
# ALERT RULE ADMIN
# ============================================================

@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "company",
        "metric",
        "operator",
        "threshold",
        "severity",
        "is_active",
        "created_at",
    )

    list_filter = (
        "company",
        "metric",
        "severity",
        "is_active",
    )

    search_fields = (
        "name",
        "company__name",
    )

    ordering = ("-created_at",)

    list_per_page = 50