from django.contrib import admin

from .models import Hackathon, UserProfile


@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date", "is_open")
    list_filter = ("is_open", "start_date")
    search_fields = ("title", "description", "location")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")
