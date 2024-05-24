import csv

from django.core.management.base import BaseCommand

from dish.models import Ingredient


class Command(BaseCommand):
    help = 'loads ingredients data from csv file'

    def handle(self, *args, **options):
        file = 'data/ingredients.csv'
        with open(file, newline='', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                name = row[0]
                measurement_unit = row[1]
                ingredient = Ingredient(
                    name=name, measurement_unit=measurement_unit
                )
                ingredient.save()
