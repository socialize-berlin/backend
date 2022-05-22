from django.db import models
import uuid

class SurveyOption(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    survey = models.ForeignKey("Survey", related_name='options', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=False)
    votes = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


    
