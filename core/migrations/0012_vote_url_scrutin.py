# Generated by Django 3.2 on 2020-10-27 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_vote_etape'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='url_scrutin',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]