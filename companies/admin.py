from django.contrib import admin

# Register your models here.
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "industry", "size", "created_at")
    search_fields = ("name",)
