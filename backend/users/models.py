from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class CustomUser(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        blank=False,
        validators=(UnicodeUsernameValidator(),)
    )
    email = models.EmailField(
        verbose_name='Адрес почты',
        max_length=254,
        unique=True,
        blank=False
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False
    )

    def __str__(self):
        return f'Пользователь {self.username}'


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='followed_users'
    )
    followed_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='following_users'
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'followed_user'),
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.followed_user}'
