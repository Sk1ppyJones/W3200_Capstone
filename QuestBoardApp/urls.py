from django.urls import path
from . import views

urlpatterns = [
    path("", views.QuestListView.as_view(), name="index"),
    path("feedback/", views.FeedbackView.as_view(), name="feedback"),
    path("feedback/success/", views.FeedbackSuccessView.as_view(), name="feedback_success"),
    path("quests/new/", views.CreateQuestView, name="create_quest"),
    path("quests/<int:pk>/", views.QuestDetailView.as_view(), name="quest_detail"),
    path("quests/<int:pk>/favorite/", views.ToggleFavoriteView, name="toggle_favorite"),
    path("my-quests/", views.MyQuestListView.as_view(), name="my_quests"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
]