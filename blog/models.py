from django.db import models
from django.contrib.auth.models import User

class BlogPost(models.Model):
    title = models.CharField(max_length=100)  # до 100 символів
    body = models.CharField(max_length=255)   # до 255 символів
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE  # якщо користувач видаляється, видаляються його пости
    )

    def __str__(self):
        return self.title  # показуємо назву поста як display name

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
