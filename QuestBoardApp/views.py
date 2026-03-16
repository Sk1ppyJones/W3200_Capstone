from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Quest
from .forms import FeedbackForm


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