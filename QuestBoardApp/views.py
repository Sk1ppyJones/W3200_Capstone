from django.shortcuts import render
from .models import Quest

# Create your views here.
def index(request):
    quests = (
        Quest.objects
        .select_related("creator", "parent")
        .prefetch_related("tags", "steps")
        .order_by("-created_at")
    )
    return render(request, "QuestBoardApp/index.html", {"quests": quests})