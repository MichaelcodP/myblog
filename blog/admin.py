from django.contrib import admin
from .models import BlogPost, Comment, UserTag


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author")
    search_fields = ("title", "body")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "body", "author", "blogpost", "created_at")
    search_fields = ("body", "author__username", "blogpost__title")
    list_filter = ("created_at",)


@admin.register(UserTag)
class UserTagAdmin(admin.ModelAdmin):
    list_display = ("id", "blogpost", "user", "created_at")
    search_fields = ("blogpost__title", "user__username")
    list_filter = ("created_at", "user")
