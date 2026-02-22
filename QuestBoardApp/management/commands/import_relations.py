import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from QuestBoardApp.models import (
    Quest,
    QuestStep,
    Participation,
    Submission,
    Team,
    TeamMembership,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Import teams, memberships, participations, and submissions from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to relations CSV.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate but do not write to the database.",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        dry_run = options["dry_run"]

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {csv_path}"))
            return

        # Caches
        users = {u.username: u for u in User.objects.all()}
        quests = {q.title: q for q in Quest.objects.all()}
        teams = {t.name: t for t in Team.objects.all()}

        created_teams = 0
        created_memberships = 0
        created_participations = 0
        created_submissions = 0

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            required = {
                "type",
                "team_name",
                "team_owner",
                "username",
                "quest_title",
                "completed",
                "xp_earned",
                "step_order",
                "submission_text",
                "approved",
            }
            missing_cols = required - set(reader.fieldnames or [])
            if missing_cols:
                self.stderr.write(self.style.ERROR(f"CSV missing columns: {sorted(missing_cols)}"))
                return

            for row in reader:
                row_type = (row["type"] or "").strip().upper()

                if row_type == "TEAM":
                    team_name = (row["team_name"] or "").strip()
                    owner_username = (row["team_owner"] or "").strip()

                    if not team_name or not owner_username:
                        self.stderr.write(self.style.ERROR("TEAM row requires team_name and team_owner."))
                        return

                    owner = users.get(owner_username)
                    if owner is None:
                        self.stderr.write(self.style.ERROR(f"User not found: '{owner_username}'"))
                        return

                    if team_name in teams:
                        continue

                    if not dry_run:
                        team = Team.objects.create(name=team_name, owner=owner)
                        teams[team_name] = team
                    created_teams += 1

                elif row_type == "TEAM_MEMBER":
                    team_name = (row["team_name"] or "").strip()
                    username = (row["username"] or "").strip()

                    team = teams.get(team_name)
                    user = users.get(username)

                    if team is None:
                        self.stderr.write(self.style.ERROR(f"Team not found: '{team_name}'"))
                        return
                    if user is None:
                        self.stderr.write(self.style.ERROR(f"User not found: '{username}'"))
                        return

                    if not dry_run and TeamMembership.objects.filter(team=team, user=user).exists():
                        continue

                    if not dry_run:
                        TeamMembership.objects.create(team=team, user=user)
                    created_memberships += 1

                elif row_type == "PARTICIPATION":
                    username = (row["username"] or "").strip()
                    quest_title = (row["quest_title"] or "").strip()

                    user = users.get(username)
                    quest = quests.get(quest_title)

                    if user is None:
                        self.stderr.write(self.style.ERROR(f"User not found: '{username}'"))
                        return
                    if quest is None:
                        self.stderr.write(self.style.ERROR(f"Quest not found: '{quest_title}'"))
                        return

                    completed = (row["completed"] or "0").strip() in ("1", "true", "True", "yes", "YES")
                    xp_earned = int((row["xp_earned"] or "0").strip())

                    if not dry_run and Participation.objects.filter(user=user, quest=quest).exists():
                        continue

                    if not dry_run:
                        Participation.objects.create(
                            user=user,
                            quest=quest,
                            completed=completed,
                            xp_earned=xp_earned,
                        )
                    created_participations += 1

                elif row_type == "SUBMISSION":
                    username = (row["username"] or "").strip()
                    quest_title = (row["quest_title"] or "").strip()
                    step_order = int((row["step_order"] or "0").strip())
                    submission_text = (row["submission_text"] or "").strip()
                    approved = (row["approved"] or "0").strip() in ("1", "true", "True", "yes", "YES")

                    user = users.get(username)
                    quest = quests.get(quest_title)

                    if user is None:
                        self.stderr.write(self.style.ERROR(f"User not found: '{username}'"))
                        return
                    if quest is None:
                        self.stderr.write(self.style.ERROR(f"Quest not found: '{quest_title}'"))
                        return

                    # Must have participation first
                    if dry_run:
                        # Can’t reliably validate in dry-run without DB writes; assume okay.
                        participation = None
                    else:
                        try:
                            participation = Participation.objects.get(user=user, quest=quest)
                        except Participation.DoesNotExist:
                            self.stderr.write(self.style.ERROR(
                                f"Missing Participation for user '{username}' in quest '{quest_title}'. "
                                f"Add PARTICIPATION row before SUBMISSION rows."
                            ))
                            return

                    # Step lookup
                    try:
                        step = QuestStep.objects.get(quest=quest, order=step_order)
                    except QuestStep.DoesNotExist:
                        self.stderr.write(self.style.ERROR(
                            f"QuestStep not found: quest '{quest_title}' step_order {step_order}"
                        ))
                        return

                    # Avoid duplicates (same participation + step + identical text)
                    if not dry_run and Submission.objects.filter(
                        participation=participation,
                        step=step,
                        text_response=submission_text,
                    ).exists():
                        continue

                    if not dry_run:
                        Submission.objects.create(
                            participation=participation,
                            step=step,
                            text_response=submission_text,
                            approved=approved,
                        )
                    created_submissions += 1

                elif not row_type:
                    # blank row
                    continue
                else:
                    self.stderr.write(self.style.ERROR(f"Unknown type: '{row_type}'"))
                    return

        if dry_run:
            self.stdout.write(self.style.SUCCESS("DRY RUN complete (no DB writes)."))

        self.stdout.write(self.style.SUCCESS(
            f"Import finished. Teams: {created_teams}, Memberships: {created_memberships}, "
            f"Participations: {created_participations}, Submissions: {created_submissions}"
        ))