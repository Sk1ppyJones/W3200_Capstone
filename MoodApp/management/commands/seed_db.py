import csv
from django.core.management.base import BaseCommand, CommandError
from MoodApp.models import JournalEntry


class Command(BaseCommand):
    help = "Seed the database from a CSV file for JournalEntry."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to CSV (e.g., data.csv)")

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                required = {"title", "entryDate", "entryText"}
                if not required.issubset(reader.fieldnames or []):
                    raise CommandError(f"CSV must contain headers: {sorted(required)}")

                created_count = 0
                for row in reader:
                    obj, created = JournalEntry.objects.get_or_create(
                        title=row["title"].strip(),
                        entryDate=row["entryDate"].strip(),
                        defaults={"entryText": row["entryText"].strip()},
                    )
                    if created:
                        created_count += 1

        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_path}")

        self.stdout.write(self.style.SUCCESS(f"Seeding complete. New entries created: {created_count}"))
