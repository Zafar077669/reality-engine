from django.contrib import admin

# Register your models here.
from .models import Actor

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "role", "active", "created_at")
    list_filter = ("role", "active")
