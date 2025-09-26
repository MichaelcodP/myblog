from django.db import models
from django.contrib.auth.models import User


class BlogPost(models.Model):
    title = models.CharField(max_length=100)  # up to 100 characters
    body = models.CharField(max_length=255)  # up to 255 characters
    author = models.ForeignKey(
        User, on_delete=models.CASCADE  # if a user is deleted, their posts are deleted
    )
    created_at = models.DateTimeField(auto_now_add=True)  # set when created
    updated_at = models.DateTimeField(auto_now=True)  # update on each save

    def __str__(self):
        return self.title  # show the post name as display name

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ["-created_at"]
