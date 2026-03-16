from django.contrib import admin
from .models import Company, CompanyMembership


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "industry", "size", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "company", "role", "created_at")
    search_fields = ("user__username", "company__name")
    list_filter = ("role", "company")