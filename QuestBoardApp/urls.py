from django.urls import path
from . import views

urlpatterns = [
    path("", views.QuestListView.as_view(), name="index"),
    path("feedback/", views.feedback_view, name="feedback"),
    path("feedback/success/", views.feedback_success, name="feedback_success"),
    path("quests/new/", views.create_quest, name="create_quest"),
    path("quests/<int:pk>/", views.QuestDetailView.as_view(), name="quest_detail"),
    path("quests/<int:pk>/favorite/", views.toggle_favorite, name="toggle_favorite"),
]