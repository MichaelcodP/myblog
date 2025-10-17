import pytest
from unittest.mock import patch
from blog.models import BlogPost
from blog.tasks import send_post_published_email
from django.contrib.auth.models import User

# -------------- Fixtures -----------------


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password")


@pytest.fixture
def blogpost(user):
    return BlogPost.objects.create(title="Test Post", body="Body", author=user)


# -------------- Tests -----------------


@pytest.mark.django_db
@patch("blog.tasks.send_mail")
def test_send_post_published_email_success(mock_send_mail, user):
    mock_send_mail.return_value = 1
    user.email = "test@example.com"
    user.save()

    post = BlogPost.objects.create(title="Test", body="Body", author=user)
    result = send_post_published_email.run(post.id)
    assert result == "Sent"
    mock_send_mail.assert_called_once()


@pytest.mark.django_db
@patch("blog.tasks.send_mail")
def test_send_post_published_email_no_email(mock_send_mail, user):
    user.email = ""
    user.save()
    post = BlogPost.objects.create(title="No Email", body="Body", author=user)
    result = send_post_published_email.run(post.id)
    assert result == "No email"
    mock_send_mail.assert_not_called()


@pytest.mark.django_db
def test_send_post_published_email_post_not_found():
    result = send_post_published_email.run(9999)
    assert result == "Post not found"
