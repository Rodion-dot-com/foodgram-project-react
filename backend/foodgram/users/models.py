from django.contrib.auth.models import AbstractUser
from django.db import models

USER_FIELD_MAX_LENGTH = 150


class User(AbstractUser):
    first_name = models.CharField(
        max_length=USER_FIELD_MAX_LENGTH,
        blank=False,
    )
    last_name = models.CharField(
        max_length=USER_FIELD_MAX_LENGTH,
        blank=False,
    )
    email = models.EmailField(
        unique=True,
    )
    REQUIRED_FIELDS = ('first_name', 'last_name', 'email')


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
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='user_following_unique',
            ),
        )
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
