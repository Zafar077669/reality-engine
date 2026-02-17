from django.contrib import admin

# Register your models here.
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "actor", "timestamp")
    list_filter = ("event_type",)
    search_fields = ("event_type",)