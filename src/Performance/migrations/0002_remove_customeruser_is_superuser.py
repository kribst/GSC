# Generated by Django 5.1.4 on 2025-03-24 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Performance', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customeruser',
            name='is_superuser',
        ),
    ]
