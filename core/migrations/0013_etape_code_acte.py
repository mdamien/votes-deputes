# Generated by Django 3.2 on 2020-10-27 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_vote_url_scrutin'),
    ]

    operations = [
        migrations.AddField(
            model_name='etape',
            name='code_acte',
            field=models.CharField(default='', max_length=40),
            preserve_default=False,
        ),
    ]
