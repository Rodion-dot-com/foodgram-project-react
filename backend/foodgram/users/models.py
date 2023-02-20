from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_CHAR_FIELD_SIZE = 150
MAX_EMAIL_FIELD_SIZE = 254


class User(AbstractUser):
    first_name = models.CharField(
        max_length=MAX_CHAR_FIELD_SIZE,
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_FIELD_SIZE,
        unique=True,
    )
    last_name = models.CharField(
        max_length=MAX_CHAR_FIELD_SIZE,
    )


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

    class Meta:
        unique_together = (
            'user',
            'following',
        )
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
