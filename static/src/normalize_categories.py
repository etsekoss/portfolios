from django.core.management.base import BaseCommand
from projects.models import Project

CATEGORY_MAP = {
    "Data Ingénierie": "data-engineering",
    "Machine Learning": "machine-learning",
    "Deep Learning": "deep-learning",
    "Stage": "stage",
}

class Command(BaseCommand):
    help = "Normalize Project.category values to slugs."

    def handle(self, *args, **options):
        updated = 0
        for p in Project.objects.all():
            old = p.category
            new = CATEGORY_MAP.get(old, old)
            if new != old:
                p.category = new
                p.save(update_fields=["category"])
                updated += 1
                self.stdout.write(f"Updated: {p.id} '{p.title}' | {old} -> {new}")
        self.stdout.write(self.style.SUCCESS(f"Done. Updated {updated} project(s)."))
