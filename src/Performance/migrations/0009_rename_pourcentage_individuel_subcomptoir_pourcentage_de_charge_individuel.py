# Generated by Django 5.1.4 on 2025-03-25 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Performance', '0008_rename_motif_quantite_importer_flyers_boncomtoir_pourcentage_individuel_quantite_importer_flyers_and'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subcomptoir',
            old_name='pourcentage_individuel',
            new_name='pourcentage_de_charge_individuel',
        ),
    ]
