from .models import Quest, QuestStep
from django import forms
from .models import Feedback
from django.forms import inlineformset_factory


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["user_name", "email", "subject", "message"]
        labels = {
            "user_name": "Your Name",
            "email": "Your Email",
            "subject": "Subject",
            "message": "Your Message",
        }
        widgets = {
            "user_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }


class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ["creator", "title", "description", "image", "parent", "tags"]
        labels = {
            "creator": "Quest Creator",
            "title": "Quest Title",
            "description": "Quest Description",
            "image": "Quest Image",
            "parent": "Parent Quest",
            "tags": "Tags",
        }
        widgets = {
            "creator": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "parent": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
        }


class QuestStepForm(forms.ModelForm):
    class Meta:
        model = QuestStep
        fields = ["instruction"]
        labels = {
            "instruction": "Step Instruction",
        }
        widgets = {
            "instruction": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


QuestStepFormSet = inlineformset_factory(
    Quest,
    QuestStep,
    form=QuestStepForm,
    extra=3,
    can_delete=False
)