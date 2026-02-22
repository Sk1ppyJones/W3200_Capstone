import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from QuestBoardApp.models import Quest, QuestStep, Tag

User = get_user_model()


class Command(BaseCommand):
    help = "Import quests + steps from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to quests CSV (one row per step).")
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

        # Cache tags by name
        tag_cache = {t.name: t for t in Tag.objects.all()}

        # Cache quests by title for parent lookup
        quest_by_title = {q.title: q for q in Quest.objects.all()}

        created_quests = 0
        created_steps = 0
        created_tags = 0
        warnings = 0

        # Group rows by quest_title (so we create each quest once)
        rows_by_quest = {}

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required = {
                "creator_username",
                "quest_title",
                "quest_description",
                "parent_title",
                "tags",
                "step_order",
                "step_instruction",
            }
            missing_cols = required - set(reader.fieldnames or [])
            if missing_cols:
                self.stderr.write(self.style.ERROR(f"CSV missing columns: {sorted(missing_cols)}"))
                return

            for row in reader:
                title = row["quest_title"].strip()
                rows_by_quest.setdefault(title, []).append(row)

        # Create/update quests then steps
        for quest_title, rows in rows_by_quest.items():
            first = rows[0]
            creator_username = first["creator_username"].strip()
            description = first["quest_description"].strip()
            parent_title = (first["parent_title"] or "").strip()
            tags_str = (first["tags"] or "").strip()

            # Validate creator exists
            try:
                creator = User.objects.get(username=creator_username)
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f"Creator username not found: '{creator_username}' (quest: '{quest_title}')"
                ))
                return

            # Parent lookup (optional)
            parent = None
            if parent_title:
                parent = quest_by_title.get(parent_title)
                if parent is None:
                    warnings += 1
                    self.stdout.write(self.style.WARNING(
                        f"Warning: parent quest not found '{parent_title}' for '{quest_title}'. Parent will be NULL."
                    ))

            # Create quest if missing
            quest = quest_by_title.get(quest_title)
            if quest is None:
                if not dry_run:
                    quest = Quest.objects.create(
                        creator=creator,
                        title=quest_title,
                        description=description,
                        parent=parent,
                    )
                else:
                    quest = Quest(creator=creator, title=quest_title, description=description, parent=parent)
                quest_by_title[quest_title] = quest
                created_quests += 1
            else:
                # Optional: keep existing quest; could update description/parent here if you want
                pass

            # Tags: create if needed + set
            tag_objs = []
            if tags_str:
                for tag_name in [t.strip() for t in tags_str.split("|") if t.strip()]:
                    tag = tag_cache.get(tag_name)
                    if tag is None:
                        if not dry_run:
                            tag = Tag.objects.create(name=tag_name)
                        else:
                            tag = Tag(name=tag_name)
                        tag_cache[tag_name] = tag
                        created_tags += 1
                    tag_objs.append(tag)

            if not dry_run and tag_objs:
                quest.tags.set(tag_objs)

            # Create steps
            for row in rows:
                order = int(row["step_order"])
                instruction = row["step_instruction"].strip()

                # Avoid duplicates if you re-run import
                if not dry_run and QuestStep.objects.filter(quest=quest, order=order).exists():
                    continue

                if not dry_run:
                    QuestStep.objects.create(quest=quest, order=order, instruction=instruction)
                created_steps += 1

        if dry_run:
            self.stdout.write(self.style.SUCCESS("DRY RUN complete (no DB writes)."))

        self.stdout.write(self.style.SUCCESS(
            f"Import finished. Quests created: {created_quests}, Steps created: {created_steps}, "
            f"Tags created: {created_tags}, Warnings: {warnings}"
        ))