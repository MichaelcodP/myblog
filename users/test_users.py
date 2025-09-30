import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# ---------- FIXTURES ----------


@pytest.fixture
def api_client():
    """Returns the REST API client."""
    return APIClient()


@pytest.fixture
def test_user():
    """Creates and returns a test user."""
    return User.objects.create_user(username="misha", password="StrongPass123")


@pytest.fixture
def refresh_token(test_user):
    """Generates a refresh token for the user."""
    return str(RefreshToken.for_user(test_user))


# ---------- REGISTER TESTS ----------


@pytest.mark.django_db
def test_register_new_user(api_client):
    data = {
        "username": "misha",
        "email": "misha@example.com",
        "password": "StrongPass123",
    }
    response = api_client.post("/api/register/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == "misha"
    assert User.objects.filter(username="misha").exists()


@pytest.mark.django_db
def test_register_existing_user(api_client, test_user):
    data = {
        "username": "misha",
        "email": "misha@example.com",
        "password": "anotherpass",
    }
    response = api_client.post("/api/register/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_without_username(api_client):
    data = {"email": "new@example.com", "password": "Pass1234"}
    response = api_client.post("/api/register/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_without_password(api_client):
    data = {"username": "newuser", "email": "new@example.com"}
    response = api_client.post("/api/register/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------- LOGIN TESTS ----------


@pytest.mark.django_db
def test_login_successful(api_client, test_user):
    data = {"username": "misha", "password": "StrongPass123"}
    response = api_client.post("/api/login/", data)
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_nonexistent_user(api_client):
    data = {"username": "no_user", "password": "Pass1234"}
    response = api_client.post("/api/login/", data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_login_wrong_password(api_client, test_user):
    data = {"username": "misha", "password": "WrongPass"}
    response = api_client.post("/api/login/", data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_empty_login_data(api_client):
    data = {"username": "", "password": ""}
    response = api_client.post("/api/login/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_without_password(api_client):
    data = {"username": "misha"}
    response = api_client.post("/api/login/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------- LOGOUT TEST ----------


@pytest.mark.django_db
def test_logout_blacklist_token(api_client, refresh_token):
    data = {"refresh": refresh_token}
    response = api_client.post("/api/token/blacklist/", data)
    assert response.status_code == status.HTTP_205_RESET_CONTENT


@pytest.mark.django_db
def test_logout_with_invalid_token(api_client):
    data = {"refresh": "this-is-an-invalid-token"}
    response = api_client.post("/api/token/blacklist/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Invalid token"
