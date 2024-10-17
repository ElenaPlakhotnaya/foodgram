import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает файлы ingredients.csv в базу данных'

    def handle(self, *args, **kwargs):
        file_path = 'data/ingredients.csv'
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                ingredient_name = row[0].strip()
                measurement_unit = row[1].strip()
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_name,
                    measurement_unit=measurement_unit
                )
                if created:
                    self.stdout.write(f'Создан ингридиент: {ingredient.name}.')
                else:
                    self.stdout.write(
                        f'Ингредиент {ingredient.name} уже существует.')
