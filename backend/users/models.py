from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        blank=False
    )
    email = models.EmailField(
        verbose_name='Адрес почты',
        max_length=254,
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


class Follow(models.Model):
    pass
