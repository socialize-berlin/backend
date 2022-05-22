from django.db import models
import uuid

class Walk(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    author = models.ForeignKey("User", related_name='invites', on_delete=models.CASCADE)
    attendees = models.ManyToManyField('User', through="WalkAttendee", related_name="walks")
    date = models.DateField()
    time = models.TimeField()
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    lng = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    
