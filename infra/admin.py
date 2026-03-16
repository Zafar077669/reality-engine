from django.contrib import admin
from .models import InfraAgent


@admin.register(InfraAgent)
class InfraAgentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company",
        "name",
        "is_active",
        "last_seen_at",
        "created_at",
    )

    list_filter = (
        "company",
        "is_active",
    )

    search_fields = (
        "name",
        "company__name",
    )

    readonly_fields = (
        "api_key",
        "created_at",
        "last_seen_at",
    )

    fieldsets = (
        (
            "Agent Info",
            {
                "fields": (
                    "company",
                    "name",
                    "is_active",
                )
            },
        ),
        (
            "Authentication",
            {
                "fields": (
                    "api_key",
                )
            },
        ),
        (
            "System",
            {
                "fields": (
                    "last_seen_at",
                    "created_at",
                )
            },
        ),
    )