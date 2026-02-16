from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    birthdate = models.DateField()
    gender = models.CharField(max_length=50)
    streak = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class Entry(models.Model):
    entryDate = models.DateField()

    class Meta:
        abstract = True   # ✅ critical


class MoodEntry(Entry):
    mood = models.IntegerField()
    notes = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.entryDate} — mood={self.mood}"


class JournalEntry(Entry):
    title = models.CharField(max_length=50)
    entryText = models.CharField(max_length=500)

    slug = models.SlugField(max_length=80, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            candidate = base
            i = 2
            while JournalEntry.objects.filter(slug=candidate).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.entryDate} — {self.title}"

    def get_absolute_url(self):
        return reverse("journal_detail", kwargs={"slug": self.slug})
