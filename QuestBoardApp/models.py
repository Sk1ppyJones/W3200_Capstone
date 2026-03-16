from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

# ChatGPT helped put the models together in time for the assignment submission this week given the project overhaul

# 1. One-to-One Relationship
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    display_name = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return self.display_name or f"Profile {self.user_id}"


# 2. Tags (Many-to-Many simple)
class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


# 3. Quests (FK + Self-Reference + M2M)
class Quest(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quests_created")

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
    created_at = models.DateTimeField(auto_now_add=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="quests")

    def __str__(self):
        return self.title


# 4. One-to-Many (Quest -> Steps)
class QuestStep(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="steps")
    order = models.PositiveIntegerField()
    instruction = models.TextField()

    def __str__(self):
        return f"{self.quest.title} - Step {self.order}"


# 5. Many-to-Many THROUGH (User <-> Quest)
class Participation(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    joined_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    xp_earned = models.IntegerField(default=0)

    class Meta:
        unique_together = ("quest", "user")

    def __str__(self):
        return f"{self.user} in {self.quest}"


# 6. Teams (Many-to-Many THROUGH)
class Team(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    members = models.ManyToManyField(User, through="TeamMembership", related_name="teams")

    def __str__(self):
        return self.name


class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "user")

    def __str__(self):
        return f"{self.user} in {self.team}"


# 7. Submissions (One-to-Many)
class Submission(models.Model):
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE, related_name="submissions")
    step = models.ForeignKey(QuestStep, on_delete=models.CASCADE)

    text_response = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Submission for {self.step}"
    
    
    
class Feedback(models.Model):
    user_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.user_name}"