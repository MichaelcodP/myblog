from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_post_published_email(self, recipient_email, post_title):
    try:
        subject = f"New Post Published: {post_title}"
        message = f"A new post titled '{post_title}' has been published on our blog."
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
    except Exception as exc:
        # Retry the task in case of failure
        raise self.retry(exc=exc, countdown=60)
