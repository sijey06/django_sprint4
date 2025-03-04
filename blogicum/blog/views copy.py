from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.http import HttpResponseForbidden
from django.views.generic import ListView, DetailView, CreateView, FormView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, ProfileForm, CommentForm

from .models import Post, Category, Profile, Comment
from .constance import COUNT_POSTS

from django.contrib.auth.mixins import UserPassesTestMixin


def update_comment_count(post):
    post.comment_count = post.comments.count()
    post.save()


def get_post_and_comment(post_id, comment_id, user):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != user:
        return post, None

    return post, comment


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        update_comment_count(post)
        return redirect('blog:post_detail', pk=post_id)

    return render(request, 'includes/comments.html', {'form': form, 'post': post})


@login_required
def edit_comment(request, post_id, comment_id):
    post, comment = get_post_and_comment(post_id, comment_id, request.user)

    if comment is None:
        return redirect('blog:post_detail', pk=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'includes/comments.html', {'form': form, 'comment': comment, 'post': post})


@login_required
def delete_comment(request, post_id, comment_id):
    post, comment = get_post_and_comment(post_id, comment_id, request.user)

    if comment is None:
        return redirect('blog:post_detail', pk=post_id)

    comment.delete()
    update_comment_count(post)

    return redirect('blog:post_detail', pk=post_id)
