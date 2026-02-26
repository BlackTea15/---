from django.contrib import admin

from .models import Hackathon


@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date", "is_open")
    list_filter = ("is_open", "start_date")
    search_fields = ("title", "description", "location")
