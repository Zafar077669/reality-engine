from django.contrib import admin

# Register your models here.
from django.utils.html import format_html

from .models import Incident, IncidentTimeline
from signals.models import Signal


# =========================
# Inlines
# =========================

class SignalInline(admin.TabularInline):
    model = Signal
    extra = 0
    can_delete = False
    readonly_fields = (
        "severity",
        "metric",
        "metric_value",
        "source",
        "created_at",
    )


class IncidentTimelineInline(admin.TabularInline):
    model = IncidentTimeline
    extra = 0
    can_delete = False
    readonly_fields = (
        "event_type",
        "message",
        "created_at",
    )


# =========================
# Incident Admin
# =========================

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company",
        "status_badge",
        "assigned_to",
        "opened_at",
        "mttr_display",
    )

    list_filter = ("status", "company")
    search_fields = ("company__name",)

    readonly_fields = (
        "opened_at",
        "investigating_at",
        "resolved_at",
        "mttr_display",
    )

    inlines = [
        SignalInline,
        IncidentTimelineInline,
    ]

    actions = [
        "action_mark_investigating",
        "action_mark_resolved",
    ]

    # =========================
    # UI Helpers
    # =========================

    def status_badge(self, obj):
        colors = {
            Incident.STATUS_OPEN: "#ff9800",
            Incident.STATUS_INVESTIGATING: "#2196f3",
            Incident.STATUS_RESOLVED: "#4caf50",
        }

        return format_html(
            '<strong style="color:{};">{}</strong>',
            colors.get(obj.status, "#9e9e9e"),
            obj.status.upper(),
        )

    status_badge.short_description = "Status"

    def mttr_display(self, obj):
        return f"{obj.mttr_minutes} min" if obj.mttr_minutes else "-"

    mttr_display.short_description = "MTTR"

    # =========================
    # Actions (SAFE)
    # =========================

    def action_mark_investigating(self, request, queryset):
        for incident in queryset:
            incident.mark_investigating()

    action_mark_investigating.short_description = "Mark as Investigating"

    def action_mark_resolved(self, request, queryset):
        for incident in queryset:
            incident.mark_resolved()

    action_mark_resolved.short_description = "Mark as Resolved"