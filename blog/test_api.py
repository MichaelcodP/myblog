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
        assert post["author_username"] == "author"


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


# ---------------------- JWT and permissions ----------------------


@pytest.mark.django_db
def test_create_post_requires_auth(api_client):
    """Unlogged user cannot create posts"""
    response = api_client.post("/api/posts/", {"title": "Test", "body": "Content"})
    assert response.status_code == 401


@pytest.mark.django_db
def test_user_can_create_post_with_token(api_client, author):
    """Logged in user can create posts"""
    api_client.force_authenticate(user=author)
    response = api_client.post("/api/posts/", {"title": "My Post", "body": "Content"})
    assert response.status_code == 201
    assert response.data["author"] == author.id
    assert BlogPost.objects.filter(title="My Post", author=author).exists()


@pytest.mark.django_db
def test_user_can_edit_own_post(api_client, author, blog_posts):
    """User can edit own post"""
    post = blog_posts[0]
    api_client.force_authenticate(user=author)
    response = api_client.put(
        f"/api/posts/{post.id}/", {"title": "Updated", "body": "Changed"}
    )
    assert response.status_code == 200
    post.refresh_from_db()
    assert post.title == "Updated"


@pytest.mark.django_db
def test_user_cannot_edit_other_post(api_client, author, another_author, blog_posts):
    """User cannot edit another user's posts"""
    post = blog_posts[0]
    api_client.force_authenticate(user=another_author)
    response = api_client.put(
        f"/api/posts/{post.id}/", {"title": "Hack", "body": "Bad"}
    )
    assert response.status_code == 403
    post.refresh_from_db()
    assert post.title != "Hack"


@pytest.mark.django_db
def test_user_cannot_delete_other_post(api_client, author, another_author, blog_posts):
    """User cannot delete another user's posts"""
    post = blog_posts[0]
    api_client.force_authenticate(user=another_author)
    response = api_client.delete(f"/api/posts/{post.id}/")
    assert response.status_code == 403
    assert BlogPost.objects.filter(id=post.id).exists()


@pytest.mark.django_db
def test_user_can_delete_own_post(api_client, author, blog_posts):
    """User can delete own post"""
    post = blog_posts[0]
    api_client.force_authenticate(user=author)
    response = api_client.delete(f"/api/posts/{post.id}/")
    assert response.status_code == 204
    assert not BlogPost.objects.filter(id=post.id).exists()
