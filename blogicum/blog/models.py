from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import PublishedModel, TitleModel
from .constance import TITLE_LENGTH, SLUG_LENGTH
from django.contrib.auth import get_user_model

# class Profile(AbstractUser):
#     def __str__(self):
#         return self.username

User = get_user_model()


class Category(PublishedModel, TitleModel):
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        max_length=SLUG_LENGTH,
        unique=True,
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, '
                   'цифры, дефис и подчёркивание.'))

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(PublishedModel):
    name = models.CharField('Название места', max_length=TITLE_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel, TitleModel):
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время '
                   'в будущем — можно делать отложенные публикации.'))
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    image = models.ImageField(
        'Изображение', upload_to='post_images', blank=True
        )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name='Категория'
    )
    comment_count = models.PositiveIntegerField(default=0,)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Комментарий', max_length=100,)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True,)
    author = models.ForeignKey(User, on_delete=models.CASCADE,)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return self.text
