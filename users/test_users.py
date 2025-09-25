from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterTestCase(APITestCase):
    def test_register_new_user(self):
        data = {
            "username": "misha",
            "email": "misha@example.com",
            "password": "StrongPass123",
        }
        response = self.client.post("/api/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "misha")
        self.assertTrue(User.objects.filter(username="misha").exists())

    def test_register_existing_user(self):
        User.objects.create_user(
            username="misha", email="misha@example.com", password="pass123"
        )
        data = {
            "username": "misha",
            "email": "misha@example.com",
            "password": "anotherpass",
        }
        response = self.client.post("/api/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_without_username(self):
        data = {"email": "new@example.com", "password": "Pass1234"}
        response = self.client.post("/api/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_without_password(self):
        data = {"username": "newuser", "email": "new@example.com"}
        response = self.client.post("/api/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="misha", password="StrongPass123")

    def test_login_successful(self):
        data = {"username": "misha", "password": "StrongPass123"}
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_nonexistent_user(self):
        data = {"username": "no_user", "password": "Pass1234"}
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_wrong_password(self):
        data = {"username": "misha", "password": "WrongPass"}
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_login_data(self):
        data = {"username": "", "password": ""}
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_without_password(self):
        data = {"username": "misha"}
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="misha", password="StrongPass123")
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(refresh)

    def test_logout_blacklist_token(self):
        data = {"refresh": self.refresh_token}
        response = self.client.post("/api/token/blacklist/", data)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
