from django.db import models

from core.models import PublishedModel, TitleModel, AuthorModel
from .constance import TITLE_LENGTH, SLUG_LENGTH, TEXT_LENGTH


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


class Post(PublishedModel, TitleModel, AuthorModel):
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время '
                   'в будущем — можно делать отложенные публикации.'))
    image = models.ImageField(
        'Изображение', upload_to='post_images', blank=True
    )
    location = models.ForeignKey(
        Location,
        related_name='posts',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        related_name='category_posts',
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    @property
    def comment_count(self):
        return self.comments.count()

    def __str__(self):
        return self.title


class Comment(AuthorModel):
    text = models.TextField('Текст комментария', max_length=TEXT_LENGTH,)
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,)
    created_at = models.DateTimeField('Создано', auto_now_add=True,)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text
