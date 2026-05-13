from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User

from .models import (
    Application,
    Hackathon,
    JuryScore,
    ProjectSubmission,
    ResultEntry,
    ScheduleItem,
    Team,
    UserProfile,
)


class StaffManagePermissionMixin:
    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_active and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(StaffManagePermissionMixin, UserAdmin):
    pass


@admin.register(Group)
class CustomGroupAdmin(StaffManagePermissionMixin, GroupAdmin):
    pass


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
    filter_horizontal = ("members",)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("hackathon", "user", "status", "created_at")
    list_filter = ("status", "hackathon")
    search_fields = ("hackathon__title", "user__username")


@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ("title", "hackathon", "starts_at", "ends_at")
    list_filter = ("hackathon",)
    search_fields = ("title", "description")


@admin.register(ResultEntry)
class ResultEntryAdmin(admin.ModelAdmin):
    list_display = ("hackathon", "place", "project_name", "team")
    list_filter = ("hackathon",)
    search_fields = ("project_name", "team__name")


@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ("title", "hackathon", "user", "team", "created_at")
    list_filter = ("hackathon",)
    search_fields = ("title", "user__username", "team__name")


@admin.register(JuryScore)
class JuryScoreAdmin(admin.ModelAdmin):
    list_display = ("submission", "jury", "score", "created_at")
    list_filter = ("score", "submission__hackathon")
    search_fields = ("submission__title", "jury__username")
