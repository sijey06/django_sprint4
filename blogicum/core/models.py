from django.db import models
from django.contrib.auth.models import User

from blog.constance import TITLE_LENGTH


class PublishedModel(models.Model):
    """Абстрактная модель. Добавляет флаг is_published и created_at."""

    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    is_published = models.BooleanField(
        'Опубликовано', default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.')

    class Meta:
        abstract = True


class TitleModel(models.Model):
    """Абстрактная модель. Добавляет Title."""

    title = models.CharField('Заголовок', max_length=TITLE_LENGTH)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class AuthorModel(models.Model):
    """Абстрактная модель. Добавляет Author."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.author
