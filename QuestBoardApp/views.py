from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Quest
from .forms import FeedbackForm, QuestForm, QuestStepFormSet, SignUpForm
from django.views.generic import FormView, ListView, DetailView, TemplateView


class FeedbackView(FormView):
    """View for feedback form"""
    template_name = "QuestBoardApp/feedback.html"
    form_class = FeedbackForm
    success_url = "/feedback/success/"
    
class FeedbackSuccessView(TemplateView):
    """View that tells user theyve submitted feedback"""
    template_name = "QuestBoardApp/feedback_success.html"


class QuestListView(ListView):
    """
    Display all quests in a gallery-style list on the home page.
    Also passes session-based favorites into the template.
    """
    model = Quest
    template_name = "QuestBoardApp/index.html"
    context_object_name = "quests"
    ordering = ["-created_at"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["favorites"] = self.request.session.get("favorites", [])
        return context


class QuestDetailView(DetailView):
    """
    Display one quest with its full description, image, tags, and steps.
    Also shows whether the quest is favorited in the current session.
    """
    model = Quest
    template_name = "QuestBoardApp/quest_detail.html"
    context_object_name = "quest"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["favorites"] = self.request.session.get("favorites", [])
        return context


@login_required
def CreateQuestView(request):
    """
    Provides the routing for creating quests and the associated form
    """
    if request.method == "POST":
        form = QuestForm(request.POST, request.FILES)
        formset = QuestStepFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            quest = form.save(commit=False)
            quest.creator = request.user
            quest.save()
            form.save_m2m()

            step_forms = formset.save(commit=False)
            for index, step in enumerate(step_forms, start=1):
                if step.instruction.strip():
                    step.quest = quest
                    step.order = index
                    step.save()

            return HttpResponseRedirect(reverse("index"))
    else:
        form = QuestForm()
        formset = QuestStepFormSet()

    return render(request, "QuestBoardApp/create_quest.html", {
        "form": form,
        "formset": formset,
    })
    
class MyQuestListView(LoginRequiredMixin, ListView):
    """View that displays the quests the logged in user has created."""
    model = Quest
    template_name = "QuestBoardApp/my_quests.html"
    context_object_name = "quests"

    def get_queryset(self):
        return Quest.objects.filter(creator=self.request.user).order_by("-created_at")


def ToggleFavoriteView(request, pk):
    """Toggle the favorite status of a quest for the current session."""
    favorites = request.session.get("favorites", [])

    if pk in favorites:
        favorites.remove(pk)
    else:
        favorites.append(pk)

    request.session["favorites"] = favorites
    request.session.modified = True

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("index")))

class SignUpView(FormView):
    """View for the signup form, and to log the user in immediately after signing up."""
    template_name = "registration/signup.html"
    form_class = SignUpForm
    success_url = "/"
# def signup_view(request):
#     """View used for the signup form, and to log the user in immediately after signing up."""
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return HttpResponseRedirect(reverse("index"))
#     else:
#         form = SignUpForm()

#     return render(request, "registration/signup.html", {"form": form})