from django.db import models
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
from api.helpers.mail import send_mail
from django.template.loader import render_to_string

class ConnectionMessage(models.Model):
    connection = models.ForeignKey("Connection", related_name='messages', on_delete=models.CASCADE)
    author = models.ForeignKey("User", related_name='+', on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)
    is_notification_sent = models.BooleanField(default=False)
    message = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True)


    
@receiver(post_save, sender=ConnectionMessage)
def send_notification(sender, instance, created, **kwargs):
    if created:
        # Check if user has unread notifications from this channel and author
        has_notification = ConnectionMessage.objects.filter(
            connection=instance.connection, 
            author=instance.author, 
            is_notification_sent=True, 
            is_seen=False
        ).exists()

        if has_notification:
            return

        interlocutor = instance.connection.invitee if instance.author == instance.connection.author else instance.connection.author
        
        context = {
            'interlocutor': interlocutor,
            'message': instance,
        }

        html_content = render_to_string(
            'api/message_notification.html', context
        )


        send_mail(
            to_emails=interlocutor.email,
            subject=f'New message from {instance.author.first_name}',
            html_content=html_content
        )

        instance.is_notification_sent = True
        instance.save()
