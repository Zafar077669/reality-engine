from django.contrib import admin
from .models import Signal


@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company",
        "response_time_ms",
        "error_rate_percent",
        "downtime_minutes",
        "severity",
        "risk_score",
        "created_at",
    )

    list_filter = ("severity", "company")
    search_fields = ("company__name",)
    ordering = ("-created_at",)