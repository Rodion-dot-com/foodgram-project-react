import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from recipes.models import Ingredient

PATH_TO_INGREDIENTS = os.path.join(
    os.path.dirname(os.path.dirname(settings.BASE_DIR)),
    'data',
    'ingredients.csv',
)


class Command(BaseCommand):
    help = 'Adds ingredients to the database'

    def handle(self, *args, **kwargs):
        with open(PATH_TO_INGREDIENTS, newline='',
                  encoding='utf-8') as csvfile:
            reader = csv.DictReader(
                csvfile,
                delimiter=',',
                fieldnames=('name', 'unit_of_measurement')
            )
            objs = (
                Ingredient(
                    name=row.get('name'),
                    unit_of_measurement=row.get('unit_of_measurement')
                ) for row in reader
            )
            try:
                Ingredient.objects.bulk_create(objs)
            except IntegrityError as e:
                self.stderr.write(self.style.WARNING(
                    f'Creation skipped. Unable to create objects. {e}'))
            else:
                self.stdout.write(self.style.SUCCESS(
                    'Ingredients added successfully'))
