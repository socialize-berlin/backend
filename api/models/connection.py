from django.db import models
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
from api.helpers.mail import send_mail
from django.template.loader import render_to_string

class Connection(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    author = models.ForeignKey("User", related_name='sent_invites', on_delete=models.CASCADE)
    invitee = models.ForeignKey("User", related_name='received_invites', on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=[('A', 'Accepted'), ('R', 'Rejected'), ('P', 'Pending')], default='P')
    author_notification_sent = models.BooleanField(default=False)
    conversation_initialised = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    
@receiver(post_save, sender=Connection)
def send_notification(sender, instance, created, **kwargs):
    if created:
        context = {
            'connection': instance,
        }

        html_content = render_to_string(
            'api/connect_notification.html', context
        )

        send_mail(
            to_emails=instance.invitee.email,
            subject=f'{instance.author.first_name} invited you to connect',
            html_content=html_content
        )

    
@receiver(post_save, sender=Connection)
def initialise_first_message(sender, instance, created, **kwargs):
    if instance.status == 'A' and not instance.conversation_initialised:
        from api.models import ConnectionMessage

        ConnectionMessage.objects.create(
            connection=instance,
            author=instance.author,
            message=instance.message
        )

        instance.conversation_initialised = True    
        instance.save()

    
@receiver(post_save, sender=Connection)
def send_status_notification(sender, instance, created, **kwargs):
    if instance.status == 'A' and not instance.author_notification_sent:
        context = {
            'connection': instance,
        }

        html_content = render_to_string(
            'api/connect_notification_status.html', context
        )

        send_mail(
            to_emails=instance.author.email,
            subject=f'Start conversation with {instance.invitee.first_name}',
            html_content=html_content
        )

        instance.author_notification_sent = True    
        instance.save()
