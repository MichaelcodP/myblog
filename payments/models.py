from django.db import models
from django.conf import settings
from blog.models import BlogPost


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    stripe_checkout_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default="usd")
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    error_message = models.TextField(blank=True, null=True)
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    refund_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ("user", "post")  # User can pay for a post only once
        indexes = [
            models.Index(fields=["stripe_checkout_id"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"Payment of {self.user} -> {self.post.title}"

    def mark_as_completed(self, intent_id=None):
        self.status = "completed"
        self.paid = True
        if intent_id:
            self.payment_intent_id = intent_id
        self.save()
