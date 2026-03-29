from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Quest
from .forms import FeedbackForm, QuestForm, QuestStepFormSet
from django.views.generic import ListView, DetailView


def index(request):
    quests = (
        Quest.objects
        .select_related("creator", "parent")
        .prefetch_related("tags", "steps")
        .order_by("-created_at")
    )
    return render(request, "QuestBoardApp/index.html", {"quests": quests})


def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("feedback_success"))
    else:
        form = FeedbackForm()

    return render(request, "QuestBoardApp/feedback.html", {"form": form})


def feedback_success(request):
    return render(request, "QuestBoardApp/feedback_success.html")


def create_quest(request):
    if request.method == "POST":
        form = QuestForm(request.POST, request.FILES)
        formset = QuestStepFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            quest = form.save()

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


class QuestListView(ListView):
    model = Quest
    template_name = "QuestBoardApp/index.html"
    context_object_name = "quests"
    ordering = ["-created_at"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["favorites"] = self.request.session.get("favorites", [])
        return context


class QuestDetailView(DetailView):
    model = Quest
    template_name = "QuestBoardApp/quest_detail.html"
    context_object_name = "quest"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["favorites"] = self.request.session.get("favorites", [])
        return context


def toggle_favorite(request, pk):
    favorites = request.session.get("favorites", [])

    if pk in favorites:
        favorites.remove(pk)
    else:
        favorites.append(pk)

    request.session["favorites"] = favorites

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("index")))
