from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, ProfileForm, CommentForm, PostForm
from django.core.exceptions import PermissionDenied
from .models import Post, Category, User, Comment
from .constance import COUNT_POSTS
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user
from django.http import Http404
from django.http import HttpResponseForbidden

def update_comment_count(post):
    post.comment_count = post.comments.count()
    post.save()


@login_required
def add_comment(request, post_id):
    """Добавляет комментарий к записи."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        update_comment_count(post)
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирует комментарий."""
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        form = CommentForm(request.POST or None, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form, 'comment': comment}
    return render(request, template, context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаляет комментарий."""
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, id=comment_id)
    post = get_object_or_404(Post, id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        comment.delete()
        update_comment_count(post)
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment}
    return render(request, template, context)


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        self.object = self.get_object()
        return (
            self.request.user.is_authenticated
            and self.object.author == self.request.user)

    def handle_no_permission(self):
        post = self.get_object()
        return HttpResponseRedirect(reverse('blog:post_detail', kwargs={'pk': post.pk}))


class RegistrationView(FormView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)


class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self,  queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Измените фильтрацию, чтобы включить все посты автора, а не только опубликованные
        user_posts = Post.objects.filter(author=self.object).order_by('-pub_date')

        paginator = Paginator(user_posts, 10)  # Измените количество постов на страницу, если требуется
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return get_object_or_404(User, username=self.request.user.username)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = super().get_object()
        if not post.is_published:
            if post.author != self.request.user:
                return HttpResponseForbidden("У вас нет доступа")
        return post

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.object.author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:index')


class PublishedPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(self.get_queryset(), id=post_id)

        if not post.is_published:
            if self.request.user != post.author:
                raise Http404("Пост недоступен.")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object.author
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        context['comment_count'] = self.object.comment_count
        return context


class CategoryListView(LoginRequiredMixin, ListView):
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
    model = Category
    template_name = 'blog/category.html'
    context_object_name = 'category'
    paginate_by = 10

    def get_object(self, queryset=None):
        category = super().get_object(queryset)
        if not category.is_published:
            raise Http404("Категория недоступна.")
        return category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем текущее время
        now = timezone.now()

        # Фильтруем посты: опубликованные и с временем публикации в прошлом
        posts = Post.objects.filter(
            category=self.object,
            is_published=True,
            pub_date__lte=now  # Добавлено условие для фильтрации по времени
        ).order_by('-pub_date')

        paginator = Paginator(posts, 10)  # 10 постов на страницу
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)  # Получаем объекты для текущей страницы
        context['page_obj'] = page_obj  # Теперь это будет обрабатывать пагинацию корректно
        return context
