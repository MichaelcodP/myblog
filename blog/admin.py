from django.contrib import admin
from .models import BlogPost, Comment


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author")
    search_fields = ("title", "body")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("body", "author", "blogpost", "created_at")
    search_fields = ("body", "author__username", "blogpost__title")
