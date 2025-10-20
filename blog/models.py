from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class BlogPost(models.Model):
    title = models.CharField(max_length=100)  # up to 100 characters
    body = models.CharField(max_length=255)  # up to 255 characters
    author = models.ForeignKey(
        User, on_delete=models.CASCADE  # if a user is deleted, their posts are deleted
    )
    created_at = models.DateTimeField(auto_now_add=True)  # set when created
    updated_at = models.DateTimeField(auto_now=True)  # update on each save

    safe_for_work = models.BooleanField(default=True)
    likes = GenericRelation("Like", related_query_name="liked_posts")

    # new field for image
    img = models.ImageField(
        upload_to="uploads/images/%Y/%m/%d/",
        blank=True,
        null=True,
    )

    # many-to-many via UserTag
    tagged_users = models.ManyToManyField(
        User, through="UserTag", related_name="tagged_posts"
    )

    premium = models.BooleanField(default=False)

    @property
    def tagged_count(self):
        return self.usertags.count()

    @property
    def last_tag_date(self):
        last_tag = self.usertags.order_by("-created_at").first()
        return last_tag.created_at if last_tag else None

    def __str__(self):
        return self.title  # show the post name as display name

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ["-created_at"]


class Comment(models.Model):
    body = models.CharField(max_length=255)
    blogpost = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="comments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    likes = GenericRelation("Like", related_query_name="liked_comments")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # for the admin panel, so that it is conveniently displayed
    def __str__(self):
        return f"Comment by {self.author or 'Anonymous'} on {self.blogpost.title}"


class UserTag(models.Model):
    blogpost = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="usertags"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usertags")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["blogpost", "user"], name="unique_user_tag")
        ]

    def __str__(self):
        return f"{self.user.username} tagged on {self.blogpost.title}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    # Generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"], name="unique_user_like"
            )
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.content_object}"
