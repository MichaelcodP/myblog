import pytest
from django.contrib.auth.models import User
from blog.models import BlogPost
from payments.models import Payment
from payments.permissions import HasPaidForPostOrIsAuthor
from rest_framework.test import APIRequestFactory


@pytest.mark.django_db
def test_author_can_access_premium_post():
    user = User.objects.create_user(username="author", password="pass")
    post = BlogPost.objects.create(
        title="Premium", body="Text", author=user, premium=True
    )
    request = APIRequestFactory().get("/")
    request.user = user

    permission = HasPaidForPostOrIsAuthor()
    assert permission.has_object_permission(request, None, post) is True


@pytest.mark.django_db
def test_user_with_payment_can_access_premium_post():
    author = User.objects.create_user(username="author", password="pass")
    user = User.objects.create_user(username="buyer", password="pass")
    post = BlogPost.objects.create(
        title="Premium", body="Text", author=author, premium=True
    )
    Payment.objects.create(
        user=user,
        post=post,
        status="completed",
        stripe_checkout_id="cs_1",
        amount=5,
        currency="usd",
    )

    request = APIRequestFactory().get("/")
    request.user = user

    permission = HasPaidForPostOrIsAuthor()
    assert permission.has_object_permission(request, None, post) is True


@pytest.mark.django_db
def test_user_without_payment_cannot_access_premium_post():
    author = User.objects.create_user(username="author", password="pass")
    user = User.objects.create_user(username="random", password="pass")
    post = BlogPost.objects.create(
        title="Premium", body="Text", author=author, premium=True
    )

    request = APIRequestFactory().get("/")
    request.user = user

    permission = HasPaidForPostOrIsAuthor()
    assert permission.has_object_permission(request, None, post) is False


@pytest.mark.django_db
def test_user_can_access_free_post():
    user = User.objects.create_user(username="user", password="pass")
    post = BlogPost.objects.create(
        title="Free", body="Text", author=user, premium=False
    )

    request = APIRequestFactory().get("/")
    request.user = user

    permission = HasPaidForPostOrIsAuthor()
    assert permission.has_object_permission(request, None, post) is True
