from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Quest, QuestStep, Feedback


# =========================
# QUEST FORM
# =========================
class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ["title", "description", "image", "parent", "tags"]
        labels = {
            "title": "Quest Title",
            "description": "Quest Description",
            "image": "Quest Image",
            "parent": "Parent Quest",
            "tags": "Tags",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "parent": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            valid_types = ["image/jpeg", "image/png", "image/webp"]
            if hasattr(image, "content_type") and image.content_type not in valid_types:
                raise ValidationError("Only JPG, PNG, or WEBP images are allowed.")
        return image


# =========================
# QUEST STEP FORM + FORMSET
# =========================
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


# =========================
# FEEDBACK FORM (OLD FEATURE)
# =========================
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


# =========================
# AUTH (SIGNUP)
# =========================
class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }