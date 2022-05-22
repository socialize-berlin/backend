from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

class CustomUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=None)

class User(AbstractUser):
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    headline = models.CharField(max_length=150, blank=True)
    introduction = models.TextField(blank=True)
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    lng = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    avatar = models.ImageField(blank=True, default='', upload_to='avatars/')
    deleted = models.DateTimeField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
