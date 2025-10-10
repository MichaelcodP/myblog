import pytest
from unittest.mock import patch
from django.contrib.auth.models import User
from blog.models import BlogPost

# -------------- Fixtures -----------------


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="password")


@pytest.fixture
def blogpost(user):
    return BlogPost.objects.create(title="Test Post", body="Body", author=user)


@pytest.mark.django_db
class TestRedisVisits:
    @patch("blog.utils.redis.Redis")
    def test_increments_visit_on_get(self, redis_mock, client, blogpost):
        # Create a fake radis instance
        redis_instance = redis_mock.return_value
        redis_instance.get.return_value = "5"  # for example 5 visits

        # Get-request to post
        url = f"/api/posts/{blogpost.pk}/"
        response = client.get(url)

        # Check that the middleware has increased the counter
        redis_instance.incr.assert_called_once_with(f"post:{blogpost.pk}:visits")
        assert response.status_code == 200

        assert response.data["visits_count"] == 5

    @patch("blog.utils.redis.Redis")
    def test_does_not_increment_on_post(self, redis_mock, client, blogpost):
        redis_instance = redis_mock.return_value

        url = f"/api/posts/{blogpost.pk}/like/"
        response = client.post(url)

        redis_instance.incr.assert_not_called()
        assert response.status_code in [200, 401, 403]

    @patch("blog.utils.redis.Redis")
    def test_returns_zero_of_no_visits(self, redis_mock, client, blogpost):
        redis_instance = redis_mock.return_value
        redis_instance.get.return_value = None

        url = f"/api/posts/{blogpost.pk}/"
        response = client.get(url)

        assert response.data["visits_count"] == 0
