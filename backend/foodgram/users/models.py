from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(max_length=150, blank=False, null=False)
    email = models.EmailField(max_length=254, blank=False, null=False)
    last_name = models.CharField(max_length=150, blank=False, null=False)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
