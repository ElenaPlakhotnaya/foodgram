import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загружает файлы tags.csv в базу данных'

    def handle(self, *args, **kwargs):
        file_path = 'data/tags.csv'
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                tag_name = row[0].strip()
                tag_slug = row[1].strip()
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    slug=tag_slug
                )
                if created:
                    self.stdout.write(f'Создан тег: {tag.name}.')
                else:
                    self.stdout.write(
                        f'Тег {tag.name} уже существует.')
