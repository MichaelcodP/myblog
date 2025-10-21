from django.db import models
from django.conf import settings
from blog.models import BlogPost


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    stripe_checkout_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default="usd")
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")  # User can pay for a post only once

    def __str__(self):
        return f"Payment of {self.user} -> {self.post.title}"
