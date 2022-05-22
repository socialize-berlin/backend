# Generated by Django 3.2.12 on 2022-03-12 09:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20220309_1023'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('A', 'Accepted'), ('R', 'Rejected'), ('P', 'Pending')], default='P', max_length=1)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_invites', to=settings.AUTH_USER_MODEL)),
                ('invitee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_invites', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
