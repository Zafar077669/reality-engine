from django.contrib import admin

# Register your models here.
from .models import Signal

@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "signal_type", "severity", "detected_at")
    list_filter = ("severity",)