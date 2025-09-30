import pytest
from django.contrib.auth.models import User
from blog.models import BlogPost
from rest_framework import status
from rest_framework.test import APIClient
from freezegun import freeze_time


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def author(db):
    return User.objects.create_user(username="author", password="pass123")


@pytest.fixture
def another_author(db):
    return User.objects.create_user(username="another_author", password="pass123")


@pytest.fixture
def blog_posts(author, another_author):
    posts = [
        BlogPost.objects.create(
            title="Safe Post 1",
            body="Safe content",
            author=author,
            safe_for_work=True,
        ),
        BlogPost.objects.create(
            title="Unsafe Post",
            body="NSFW",
            author=author,
            safe_for_work=False,
        ),
        BlogPost.objects.create(
            title="Another Author's Post",
            body="Other content",
            author=another_author,
            safe_for_work=True,
        ),
    ]
    return posts


@pytest.mark.django_db
def test_filter_safe_for_work(api_client, blog_posts):
    response = api_client.get("/api/posts/?safe_for_work=True")
    assert response.status_code == status.HTTP_200_OK
    for post in response.data["results"]:
        assert post["safe_for_work"] is True


@pytest.mark.django_db
def test_filter_by_author(api_client, blog_posts):
    response = api_client.get("/api/posts/?author=author")
    assert response.status_code == status.HTTP_200_OK
    for post in response.data["results"]:
        assert post["author"] == "author"


@pytest.mark.django_db
def test_searching_by_title(api_client, blog_posts):
    response = api_client.get("/api/posts/?search=Safe")
    assert response.status_code == status.HTTP_200_OK
    titles = [post["title"] for post in response.data["results"]]
    assert any("Safe" in t for t in titles)


@pytest.mark.django_db
def test_ordering_by_title(api_client, blog_posts):
    response = api_client.get("/api/posts/?ordering=title")
    assert response.status_code == status.HTTP_200_OK
    titles = [p["title"] for p in response.data["results"]]
    assert titles == sorted(titles)


@pytest.mark.django_db
@freeze_time("2025-01-01")
def test_filter_created_at_range(api_client, author):
    # create a post on a specific date
    BlogPost.objects.create(
        title="Post in range",
        body="Body",
        author=author,
        safe_for_work=True,
    )
    response = api_client.get(
        "/api/posts/?created_at_after=2024-12-31&created_at_before=2025-01-02"
    )
    assert response.status_code == status.HTTP_200_OK
    assert any("Post in range" in p["title"] for p in response.data["results"])


@pytest.mark.django_db
def test_pagination_structure(api_client, blog_posts):
    response = api_client.get("/api/posts/")
    assert "count" in response.data
    assert "results" in response.data
