# Generated by Django 3.2 on 2020-10-26 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_dossier_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dossier',
            name='slug',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
