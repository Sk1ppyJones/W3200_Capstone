from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

# Create your views here.
def index_view(request):
    return HttpResponse(f"""
                        <h1> 
                            MoodFlow
                        </h1>
                        <p>MoodFlow is an app meant to allow
                        the user to keep track of there current
                        moods and act as a virtual journal. The
                        hopeful goal of it is to help me keep track
                        of manic episodes to talk to my therapist
                        about :D</P
                        """)