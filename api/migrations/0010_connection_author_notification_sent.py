# Generated by Django 3.2.12 on 2022-05-08 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_connectionmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='connection',
            name='author_notification_sent',
            field=models.BooleanField(default=False),
        ),
    ]
