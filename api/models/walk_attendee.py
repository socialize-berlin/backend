from django.db import models


class WalkAttendee(models.Model):
    walk = models.ForeignKey("Walk", on_delete=models.CASCADE)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    
