from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index_view, name="Home"),
    path('about/', views.about_view, name="About"),
    path("journal/<slug:slug>/", views.journal_detail, name="journal_detail"),
]
