# Generated by Django 3.2.12 on 2022-05-21 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_survey_is_featured'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveyoption',
            name='votes',
            field=models.IntegerField(default=0),
        ),
    ]
