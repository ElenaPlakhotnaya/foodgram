from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint

from users.constants import EMEIL_LENGTH, NAME_LENGTH


class User(AbstractUser):
    email = models.EmailField(
        'Адрес эл.почты', max_length=EMEIL_LENGTH, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password',
    )

    avatar = models.ImageField(
        blank=True, null=True, upload_to='users/avatar/')
    username = models.CharField(
        'Логин', max_length=NAME_LENGTH, unique=True, blank=False)
    first_name = models.CharField('Имя', max_length=NAME_LENGTH, blank=False)
    last_name = models.CharField(
        'Фамилия', max_length=NAME_LENGTH, blank=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriber')
    subscribing = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribing')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'subscribing'], name='unique_together'
            ),
            CheckConstraint(
                check=~Q(user=F('subscribing')),
                name='chek_self_subscription'
            )
        ]
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.subscribing}'
