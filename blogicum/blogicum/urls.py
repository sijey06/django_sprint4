from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler500, handler404
from django.urls import include, path

from blog.views import RegistrationView


urlpatterns = [
    path('pages/', include('pages.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/',
         RegistrationView.as_view(), name='registration'),
    path('', include('blog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.error500'
