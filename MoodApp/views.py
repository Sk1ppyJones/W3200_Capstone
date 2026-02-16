from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest
from .models import JournalEntry

# Create your views here.


def index_view(request):
    entries = JournalEntry.objects.all().order_by("-entryDate")
    return render(request, "MoodApp/index.html", {"entries": entries})


def about_view(request):
    return render(request, 'MoodApp/about.html')


def journal_detail(request, slug):
    entry = get_object_or_404(JournalEntry, slug=slug)
    return render(request, "MoodApp/detail.html", {"entry": entry})
