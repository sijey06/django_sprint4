from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden

from .constance import PAGINATE_COUNT
from .models import Post


class PostCheckMixin:
    """Mixin для проверки прав доступа к посту."""

    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_object(self):
        post = super().get_object()
        self.check_permissions(post)
        return post

    def check_permissions(self, post):
        if not post.is_published and post.author != self.request.user:
            raise HttpResponseForbidden("У вас нет доступа")

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs['post_id'])
        if self.object.author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostMixin:
    """Mixin для модели Post."""

    model = Post


def paginate_queryset(queryset, request):
    """Функция для пагинации переданного queryset."""
    paginator = Paginator(queryset, PAGINATE_COUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
