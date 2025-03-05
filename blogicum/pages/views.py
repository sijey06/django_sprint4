from django.views.generic import TemplateView
from django.shortcuts import render

from blog.constance import ST_NOT_FOUND, ST_CSRF, ST_ERR


def page_not_found(request, exception):
    """Обработчик для страницы 404 Not Found."""
    return render(request, 'pages/404.html', status=ST_NOT_FOUND)


def csrf_failure(request, reason=''):
    """Обработчик для ошибки CSRF."""
    return render(request, 'pages/403csrf.html', status=ST_CSRF)


def error500(request, *args, **kwargs):
    """Обработчик для серверной ошибки 500."""
    return render(request, 'pages/500.html', status=ST_ERR)


class About(TemplateView):
    """Отображает страницу "О проекте"."""

    template_name = 'pages/about.html'


class Rules(TemplateView):
    """Отображает страницу "Наши правила"."""

    template_name = 'pages/rules.html'
