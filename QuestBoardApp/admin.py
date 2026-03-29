from django.contrib import admin
from .models import (
    UserProfile,
    Tag,
    Quest,
    QuestStep,
    Participation,
    Team,
    TeamMembership,
    Submission,
    Feedback,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "display_name")
    search_fields = ("display_name", "user__username", "user__email")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class QuestStepInline(admin.TabularInline):
    model = QuestStep
    extra = 1


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    """
    Primary entity admin customization (per assignment):
    - list_display
    - list_filter
    - search_fields
    """
    list_display = ("id", "title", "creator", "parent", "created_at")
    list_filter = ("created_at", "tags")
    search_fields = ("title", "description", "creator__username")
    inlines = [QuestStepInline]


@admin.register(QuestStep)
class QuestStepAdmin(admin.ModelAdmin):
    list_display = ("id", "quest", "order")
    list_filter = ("quest",)
    search_fields = ("quest__title", "instruction")


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "quest", "completed", "xp_earned", "joined_at")
    list_filter = ("completed", "joined_at")
    search_fields = ("user__username", "quest__title")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner")
    search_fields = ("name", "owner__username")


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "team", "user", "joined_at")
    list_filter = ("team", "joined_at")
    search_fields = ("team__name", "user__username")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "participation", "step", "approved", "submitted_at")
    list_filter = ("approved", "submitted_at")
    search_fields = ("participation__user__username", "participation__quest__title", "step__quest__title")
    
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "user_name", "email", "subject", "submitted_at")
    list_filter = ("submitted_at",)
    search_fields = ("user_name", "email", "subject", "message")
    
