from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

# Create your views here.
def index_view(request):
    return render(request, 'MoodApp/index.html')

def about_view(request):
    return render(request, 'MoodApp/about.html')