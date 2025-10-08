import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Like, BlogPost, Comment
from rest_framework.test import APIClient


# -------------- Fixtures -----------------
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password")


@pytest.fixture
def blogpost(user):
    return BlogPost.objects.create(title="Test Post", body="Body", author=user)


@pytest.fixture
def comment(user, blogpost):
    return Comment.objects.create(body="Comment", blogpost=blogpost, author=user)


# -------------- Tests -----------------


@pytest.mark.django_db
class TestLikesSystem:
    def test_user_can_like_and_unlike_post(self, api_client, user, blogpost):
        api_client.force_authenticate(user=user)

        url_like = reverse("post-like", args=[blogpost.id])
        url_unlike = reverse("post-unlike", args=[blogpost.id])

        # Like post
        res_like = api_client.post(url_like)
        assert res_like.status_code == 200
        assert res_like.data["status"] == "liked"
        assert Like.objects.filter(user=user, object_id=blogpost.id).exists()

        # Unlike post
        res_unlike = api_client.post(url_unlike)
        assert res_unlike.status_code == 200
        assert res_unlike.data["status"] == "unliked"
        assert not Like.objects.filter(user=user, object_id=blogpost.id).exists()

    def test_user_cannot_like_same_post_twice(self, api_client, user, blogpost):
        api_client.force_authenticate(user=user)
        url_like = reverse("post-like", args=[blogpost.id])

        api_client.post(url_like)
        res = api_client.post(url_like)

        assert res.data["status"] == "already liked"
        assert Like.objects.filter(user=user, object_id=blogpost.id).count() == 1

    def test_user_can_like_comment(self, api_client, user, comment):
        api_client.force_authenticate(user=user)

        url_like = reverse("comment-like", args=[comment.id])
        res = api_client.post(url_like)

        assert res.status_code == 200
        assert res.data["status"] == "liked"
        assert Like.objects.filter(user=user, object_id=comment.id).exists()

    def test_unauthenticated_user_cannot_like_post(self, blogpost):
        client = APIClient()  # without authorization
        url = reverse("post-like", args=[blogpost.id])
        response = client.post(url)
        assert response.status_code == 401
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_unauthenticated_user_cannot_unlike_post(self, blogpost):
        client = APIClient()
        url = reverse("post-like", args=[blogpost.id])
        response = client.post(url)
        assert response.status_code == 401
