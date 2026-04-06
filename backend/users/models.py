from core.constants import SLICE_OUTPUT_STR_METHOD
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import USER_MAX_LENGTH_CHARFIELD, USER_MAX_LENGTH_EMAILFIELD
from .validators import check_username


class User(AbstractUser):
    """Описывает кастомную модель пользователя.

    Расширяет стандартную модель AbstractUser.
    - переопределено поле username, сделано в качестве уникального
    и обязательного;
    - переопределно поле email, сделано в качестве обязательного и уникального;
    - переопределяет поля first_name и last_name, сделано
    в качестве обязательного;
    - добавлено поле is_subscribed;
    - добавлено поле avatar для хранения фото/изображения пользователя;
    - установлена недопустимость повторной регистрации пользователя.
    """

    username = models.CharField(
        max_length=USER_MAX_LENGTH_CHARFIELD,
        blank=False,
        unique=True,
        validators=(check_username,),
        verbose_name='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=USER_MAX_LENGTH_CHARFIELD,
        blank=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USER_MAX_LENGTH_CHARFIELD,
        blank=False,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        max_length=USER_MAX_LENGTH_EMAILFIELD,
        unique=True,
        blank=False,
        verbose_name='Email'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        default=None,
        verbose_name='Аватар'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user',
                violation_error_message=(
                    'Пользователь с таким username и email существует.'
                )
            ),
        )
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:SLICE_OUTPUT_STR_METHOD]


class Subscriptions(models.Model):
    """Модель подписки на пользователя.

    В модели установлены ограничения, по которым пользователь
    не может подпиаться на самого себя, а также не может повторно подписаться
    на другого пользователя.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscriptions'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='На кого подписан',
        related_name='followers'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_subscriptions',
                violation_error_message='Вы уже подписаны на пользователя.'
            ),
            models.CheckConstraint(
                condition=~models.Q(user=models.F('following')),
                name='dont_self_follow',
                violation_error_message='Подписка на себя не допустима.'

            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
