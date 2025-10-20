import logging
from blog.models import BlogPost
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_post_published_email(self, post_id):
    """
    Asynchronous task to send an email notif when a new post is published
    """
    try:
        post = BlogPost.objects.get(id=post_id)
        user_email = post.author.email

        if not user_email:
            logger.warning(f"User for post {post_id} has no email")
            return "No email"

        subject = f"New Post Published: {post.title}"
        message = f"Hello {post.author.username},\n\nYour post '{post.title}' has been published."
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")

        send_mail(
            subject,
            message,
            from_email,
            [user_email],
            fail_silently=False,
        )

        logger.info(f"Email sent successfully to {user_email} for post {post_id}")

        return "Sent"

    except BlogPost.DoesNotExist:
        logger.error(f"Post {post_id} does not exist")
        return "Post not found"
    except Exception as e:
        logger.error(f"Error sending email for post {post_id}: {e}")
        # Retry the task in case of failure
        raise self.retry(exc=e)
