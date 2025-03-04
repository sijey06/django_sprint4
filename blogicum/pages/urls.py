from .views import About, Rules

from django.urls import path


app_name = 'pages'

urlpatterns = [
    path('about/', About.as_view(), name='about'),
    path('rules/', Rules.as_view(), name='rules'),
]
