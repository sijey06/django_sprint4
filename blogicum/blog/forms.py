from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'image',
            'location',
            'category',
            'is_published'
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M', attrs={'type': 'datetime-local'}
            )
        }
