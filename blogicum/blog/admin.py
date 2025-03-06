from django.contrib import admin

from .models import Post, Category, Location, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'category', 'location', )
    list_filter = ('author', 'category', 'location', 'pub_date')
    search_fields = ('title', 'text', 'author__username')
    ordering = ('-pub_date',)
    inlines = (CommentInline,)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'text', 'post',)
