# Generated by Django 4.2.16 on 2024-10-16 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='short_link',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True),
        ),
    ]
