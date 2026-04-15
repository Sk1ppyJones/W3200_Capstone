from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL

# ChatGPT helped put the models together in time for the assignment submission this week given the project overhaul

# 1. One-to-One Relationship


class UserProfile(models.Model):
    """User profile extending the default Django User model with additional info"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    display_name = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return self.display_name or f"Profile {self.user_id}"


# 2. Tags (Many-to-Many simple)
class Tag(models.Model):
    """Tags given to quests for categorization and discovery"""
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


# 3. Quests (FK + Self-Reference + M2M)
class Quest(models.Model):
    """The main entity of the site, representing a quest created by users."""
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="quests_created")

    # Self-referential relationship (remix/fork)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="remixes"
    )

    title = models.CharField(max_length=120)
    description = models.TextField()
    image = models.ImageField(
        upload_to="quest_images/", blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="quests")

    def __str__(self):
        return self.title


# 4. One-to-Many (Quest -> Steps)
class QuestStep(models.Model):
    """The Different Steps in Quests"""
    quest = models.ForeignKey(
        Quest, on_delete=models.CASCADE, related_name="steps")
    order = models.PositiveIntegerField()
    instruction = models.TextField()

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["quest", "order"], name="unique_step_order_per_quest")]

    def __str__(self):
        return f"{self.quest.title} - Step {self.order}"


# 5. Many-to-Many THROUGH (User <-> Quest)
class Participation(models.Model):
    """Who participates in a quest and their progress"""
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    joined_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    xp_earned = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["quest", "user"], name="unique_participation")]

    def __str__(self):
        return f"{self.user.username} in {self.quest}"


# 6. Teams (Many-to-Many THROUGH)
class Team(models.Model):
    """The DIfferent 'teams' on the site for friends"""
    name = models.CharField(max_length=80)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        User, through="TeamMembership", related_name="teams")
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class TeamMembership(models.Model):
    """Defines relationship between users and teams"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["team", "user"], name="unique_team_membership")
        ]

    def __str__(self):
        return f"{self.user} in {self.team}"


# 7. Submissions (One-to-Many)
class Submission(models.Model):
    """User submissions for quest steps, with approval workflow"""
    participation = models.ForeignKey(
        Participation, on_delete=models.CASCADE, related_name="submissions")
    step = models.ForeignKey(QuestStep, on_delete=models.CASCADE)

    text_response = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=False)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["participation", "step"], name="unique_submission_per_step")
        ]
    
    def clean(self):
        if self.step.quest_id != self.participation.quest_id:
            raise ValidationError("Submission step must belong to the same quest as the participation.")

    def __str__(self):
        return f"{self.participation.user.username} - {self.step}"


class Feedback(models.Model):
    """Feedback users can submit for site improvement"""
    user_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.user_name}"
