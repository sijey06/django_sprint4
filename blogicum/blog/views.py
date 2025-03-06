from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    FormView,
    UpdateView,
    DeleteView
)
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.urls import reverse_lazy, reverse

from .constance import PAGINATE_COUNT
from .check_comments import (
    get_comment_and_check_permission,
    render_comment_template,
    get_post
)
from .forms import RegisterForm, ProfileForm, CommentForm, PostForm
from .mixins import PostCheckMixin, PostMixin, paginate_queryset
from .models import Post, Category


@login_required
def add_comment(request, post_id):
    """Добавляет комментарий к записи."""
    post = get_post(post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирует комментарий."""
    comment = get_comment_and_check_permission(request, comment_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = CommentForm(instance=comment)

    return render_comment_template(request, comment, form)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаляет комментарий."""
    comment = get_comment_and_check_permission(request, comment_id)
    get_post(post_id)

    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id)

    return render_comment_template(request, comment, None)


@login_required
def post_list(request):
    """Список всех постов с количеством комментариев."""
    posts = Post.objects.annotate(comment_count=Count('comments'))

    return render(request, 'includes/post_card.html', {'posts': posts})


class RegistrationView(FormView):
    """Отображение страницы регистрации."""

    template_name = 'registration/registration_form.html'
    form_class = RegisterForm
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ProfileDetailView(DetailView):
    """Отображение страницы профиля."""

    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_posts = Post.objects.filter(
            author=self.object
        ).order_by('-pub_date')
        context['page_obj'] = paginate_queryset(user_posts, self.request)
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Отображение страницы редактирования профиля."""

    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return get_object_or_404(User, username=self.request.user.username)


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    """Отображение страницы создания поста."""

    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class PostUpdateView(LoginRequiredMixin, PostMixin,
                     PostCheckMixin, UpdateView):
    """Отображение страницы редактирования поста."""

    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.pk_url_kwarg]}
        )


class PostDeleteView(LoginRequiredMixin, PostMixin,
                     PostCheckMixin, DeleteView):
    """Страница удаления поста."""

    def get_success_url(self):
        return reverse('blog:index')


class PublishedPostsView(LoginRequiredMixin, PostMixin, ListView):
    """Отображает главную страницу с постами."""

    template_name = 'blog/index.html'
    paginate_by = PAGINATE_COUNT

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )


class PostDetailView(LoginRequiredMixin, PostMixin, DetailView):
    """Отображает страницу поста."""

    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(self.get_queryset(), id=post_id)

        if not post.is_published:
            if self.request.user != post.author:
                raise Http404('Пост недоступен.')
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object.author
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        context['comment_count'] = self.object.comments.count()
        return context


class CategoryListView(LoginRequiredMixin, ListView):
    """Список категорий."""

    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'categories'

    def get_queryset(self):
        user = self.request.user
        published_posts = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
        user_posts = Post.objects.filter(
            author=user,
            is_published=False
        )
        return published_posts | user_posts


class CategoryDetailView(LoginRequiredMixin, DetailView):
    """Отображает страницу с постами выбранной категории."""

    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'category'

    def get_object(self, queryset=None):
        category = super().get_object(queryset)
        if not category.is_published:
            raise Http404('Категория недоступна.')
        return category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        posts = Post.objects.filter(
            category=self.object,
            is_published=True,
            pub_date__lte=now
        ).order_by('-pub_date')
        context['page_obj'] = paginate_queryset(posts, self.request)
        return context
