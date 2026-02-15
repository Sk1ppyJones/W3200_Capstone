from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=50)
    birthdate = models.DateField()
    gender = models.CharField(max_length=50)
    streak = models.IntegerField(default=0)

    def __str__(self):
        return (f"User: {self.name}\nID: {self.userID}\nBirthdate: {self.birthdate} \nGender: {self.gender}\nMood Streak: {self.streak}")


class Entry(models.Model):
    entryDate = models.DateField()


class MoodEntry(Entry):
    # Thinking, each mood has a numeric 1-10 and then it assigns based off that
    mood = models.IntegerField()
    notes = models.CharField(max_length=120)

    def __str__(self):
        return (f'Entry ID: {self.ID}\nMood: {self.mood}\nNotes: {self.notes}')


class JournalEntry(Entry):
    title = models.CharField(max_length=50)
    entryText = models.CharField(max_length=500)

    def __str__(self):
        return (f'Entry ID: {self.ID}\nTitle: {self.title}\n{self.entryText}')
