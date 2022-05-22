from django.db import models
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
from api.helpers.mail import send_mail
from django.template.loader import render_to_string

class Message(models.Model):
    name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(blank=False)
    message = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True)

    
@receiver(post_save, sender=Message)
def send_notification(sender, instance, created, **kwargs):
    if created:
        context = {
            'message': instance,
        }

        html_content = render_to_string(
            'api/contact_message_notification.html', context
        )

        send_mail(
            to_emails="me@andrewtolochka.com",
            subject=f'New contact message from {instance.name}',
            html_content=html_content
        )
