# Generated by Django 5.1.4 on 2025-03-24 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Performance', '0004_remove_customeruser_is_superuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeruser',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
    ]
