from django.contrib import admin

from .models import Application, Hackathon, Team, UserProfile


@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date", "application_deadline", "max_participants", "is_open")
    list_filter = ("is_open", "start_date", "application_deadline")
    search_fields = ("title", "description", "location")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "hackathon", "captain", "invite_code")
    list_filter = ("hackathon",)
    search_fields = ("name", "captain__username", "invite_code")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("hackathon", "user", "status", "created_at")
    list_filter = ("status", "hackathon")
    search_fields = ("hackathon__title", "user__username")
