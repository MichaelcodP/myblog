from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# ---------- Register ----------
class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]  # opens registration without authorization

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Create a new user account with username, email, and password",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User created successfully",
                examples={
                    "application/json": {
                        "username": "example_user",
                        "email": "user@example.com",
                    }
                },
            ),
            400: "Invalid input",
        },
        tags=["authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# ---------- Login ----------
class LoginView(APIView):
    """
    API endpoint for user login.
    """

    permission_classes = [AllowAny]  # opens login without authorization

    @swagger_auto_schema(
        operation_summary="Log in a user",
        operation_description="Authenticate user and return JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "refresh": "jwt-refresh-token",
                        "access": "jwt-access-token",
                    }
                },
            ),
            400: "Missing credentials",
            401: "Invalid credentials",
        },
        tags=["authentication"],
    )
    def post(self, request):
        """Authenticate user and return JWT tokens."""
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


# ---------- Logout ----------
class LogoutView(TokenBlacklistView):
    """
    API endpoint for user logout.
    """

    @swagger_auto_schema(
        operation_summary="Log out a user",
        operation_description="Blacklist the user's refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="JWT refresh token to blacklist",
                )
            },
        ),
        responses={
            205: "Successfully logged out",
            400: "Invalid token or token required",
        },
        tags=["authentication"],
    )
    def post(self, request):
        """Blacklist the user's refresh token."""
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response(
                {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
