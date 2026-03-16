from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("feedback/", views.feedback_view, name="feedback"),
    path("feedback/success/", views.feedback_success, name="feedback_success"),
]