from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Quest, Team, TeamMembership
from .forms import FeedbackForm, QuestForm, QuestStepFormSet, SignUpForm, TeamForm
from django.views.generic import FormView, ListView, DetailView, TemplateView
from django.contrib import messages


class FeedbackView(FormView):
    """View for feedback form"""
    template_name = "QuestBoardApp/feedback.html"
    form_class = FeedbackForm
    success_url = "/feedback/success/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class FeedbackSuccessView(TemplateView):
    """View that tells user theyve submitted feedback"""
    template_name = "QuestBoardApp/feedback_success.html"


class QuestListView(ListView):
    """
    Display all quests in a gallery-style list on the home page.
    Also passes session-based favorites into the template.
    """
    model = Quest
    template_name = "QuestBoardApp/index.html"
    context_object_name = "quests"
    ordering = ["-created_at"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["favorites"] = self.request.session.get("favorites", [])
        return context


class QuestDetailView(DetailView):
    """
    Display one quest with its full description, image, tags, and steps.
    Also shows whether the quest is favorited in the current session.
    """
    model = Quest
    template_name = "QuestBoardApp/quest_detail.html"
    context_object_name = "quest"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["favorites"] = self.request.session.get("favorites", [])
        return context


@login_required
def CreateQuestView(request):
    """
    Provides the routing for creating quests and the associated form
    """
    if request.method == "POST":
        form = QuestForm(request.POST, request.FILES)
        formset = QuestStepFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            quest = form.save(commit=False)
            quest.creator = request.user
            quest.save()
            form.save_m2m()

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


class MyQuestListView(LoginRequiredMixin, ListView):
    """View that displays the quests the logged in user has created."""
    model = Quest
    template_name = "QuestBoardApp/my_quests.html"
    context_object_name = "quests"

    def get_queryset(self):
        return Quest.objects.filter(creator=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["favorites"] = self.request.session.get("favorites", [])
        return context  # TODO


@require_POST
def ToggleFavoriteView(request, pk):
    """Toggle the favorite status of a quest for the current session."""
    quest = get_object_or_404(Quest, pk=pk)
    favorites = request.session.get("favorites", [])

    if pk in favorites:
        favorites.remove(pk)
    else:
        favorites.append(pk)

    request.session["favorites"] = favorites
    request.session.modified = True
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("index")))


class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = SignUpForm
    success_url = "/"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.get.success_url())

# Team Views


class TeamListView(ListView):
    model = Team
    template_name = "QuestBoardApp/team_list.html"
    context_object_name = "teams"
    ordering = ["name"]


class TeamDetailView(DetailView):
    model = Team
    template_name = "QuestBoardApp/team_detail.html"
    context_object_name = "team"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        team = self.object

        context["memberships"] = team.memberships.select_related(
            "user").order_by("joined_at")
        context["is_member"] = user.is_authenticated and team.members.filter(
            pk=user.pk).exists()
        context["is_owner"] = user.is_authenticated and team.owner_id == user.id

        current_membership = None
        if user.is_authenticated:
            current_membership = TeamMembership.objects.filter(
                user=user).select_related("team").first()

        context["current_membership"] = current_membership
        return context


@login_required
def create_team(request):
    existing_membership = TeamMembership.objects.filter(
        user=request.user).first()
    if existing_membership:
        messages.error(
            request, "You are already on a team. Leave your current team before creating a new one.")
        return redirect("team_detail", pk=existing_membership.team.pk)

    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.owner = request.user
            team.save()

            TeamMembership.objects.create(team=team, user=request.user)

            messages.success(request, "Team created successfully.")
            return redirect("team_detail", pk=team.pk)
    else:
        form = TeamForm()

    return render(request, "QuestBoardApp/create_team.html", {"form": form})


@login_required
@require_POST
def join_team(request, pk):
    team = get_object_or_404(Team, pk=pk)

    existing_membership = TeamMembership.objects.filter(
        user=request.user).select_related("team").first()

    if existing_membership:
        if existing_membership.team_id == team.pk:
            messages.info(request, f"You are already a member of {team.name}.")
        else:
            messages.error(
                request,
                f"You are already a member of {existing_membership.team.name}. Leave your current team before joining another."
            )
        return redirect("team_detail", pk=team.pk)

    TeamMembership.objects.create(team=team, user=request.user)
    messages.success(request, f"You joined {team.name}.")
    return redirect("team_detail", pk=team.pk)


@login_required
@require_POST
def leave_team(request, pk):
    team = get_object_or_404(Team, pk=pk)

    membership = TeamMembership.objects.filter(
        team=team, user=request.user).first()

    if not membership:
        messages.error(request, "You are not a member of this team.")
        return redirect("team_detail", pk=team.pk)

    if team.owner_id == request.user.id:
        messages.error(request, "Team owners cannot leave their own team.")
        return redirect("team_detail", pk=team.pk)

    membership.delete()
    messages.success(request, f"You left {team.name}.")
    return redirect("team_list")

class MyTeamView(LoginRequiredMixin, TemplateView):
    template_name = "QuestBoardApp/my_team.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        membership = TeamMembership.objects.filter(user=self.request.user).select_related("team").first()
        context["membership"] = membership
        return context