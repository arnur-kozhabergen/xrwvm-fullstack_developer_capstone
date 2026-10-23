import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from djangoapp.models import CarMake, CarModel


class Command(BaseCommand):
    help = (
        "Idempotently load the supplied course car dataset; never delete existing data."
    )

    def handle(self, *args, **options):
        rows = json.loads(
            (Path(settings.BASE_DIR) / "database/data/car_records.json").read_text(
                encoding="utf-8"
            )
        )["cars"]
        for row in rows:
            make, _ = CarMake.objects.get_or_create(name=row["make"])
            CarModel.objects.get_or_create(
                car_make=make,
                name=row["model"],
                year=row["year"],
                defaults={"type": row["bodyType"]},
            )
        self.stdout.write(
            f"Car makes: {CarMake.objects.count()}; "
            f"car models: {CarModel.objects.count()}"
        )
