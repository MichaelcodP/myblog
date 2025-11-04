import pytest
import stripe
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient
from blog.models import BlogPost
from payments.models import Payment
from django.contrib.auth.models import User


@pytest.mark.django_db
@patch("stripe.checkout.Session.create")
def test_create_checkout_session_success(mock_stripe_session):
    # Author
    author = User.objects.create_user(
        username="author", password="12345", email="author@example.com"
    )

    # Customer
    customer = User.objects.create_user(
        username="customer", password="12345", email="customer@example.com"
    )

    client = APIClient()
    client.force_authenticate(user=customer)  # Authenticate as customer

    post = BlogPost.objects.create(
        title="Premium post",
        body="Some content",
        author=author,  # Post is created by author
        premium=True,
    )

    mock_stripe_session.return_value = MagicMock(id="cs_test_123")

    url = reverse("payments:create_checkout_session", args=[post.id])
    response = client.post(url)

    assert response.status_code == 200
    assert "id" in response.data
    assert response.data["id"] == "cs_test_123"

    payment = Payment.objects.first()
    assert payment is not None
    assert payment.user == customer  # Check payment is for customer
    assert payment.post == post
    assert payment.status == "pending"


@pytest.mark.django_db
def test_create_checkout_session_non_premium():
    user = User.objects.create_user(username="misha", password="12345")
    client = APIClient()
    client.force_authenticate(user=user)

    post = BlogPost.objects.create(
        title="Free post", body="Text", author=user, premium=False
    )
    url = reverse("payments:create_checkout_session", args=[post.id])
    response = client.post(url)

    assert response.status_code == 400
    assert "not premium" in response.data["error"]


@pytest.mark.django_db
def test_author_access_own_premium_post():
    author = User.objects.create_user(username="author", password="pass")
    client = APIClient()
    client.force_authenticate(user=author)

    post = BlogPost.objects.create(
        title="Premium", body="Body", author=author, premium=True
    )
    url = reverse("payments:create_checkout_session", args=[post.id])
    response = client.post(url)

    assert response.status_code == 200
    assert "Authors can access" in response.data["message"]


@pytest.mark.django_db
def test_already_purchased():
    # Create AUTHOR (different user)
    author = User.objects.create_user(username="author", password="pass")

    # Create BUYER (the one who purchased)
    buyer = User.objects.create_user(username="buyer", password="pass")
    client = APIClient()
    client.force_authenticate(user=buyer)  # Authenticate as BUYER

    post = BlogPost.objects.create(
        title="Premium post",
        body="Body",
        author=author,
        premium=True,  # Author is different
    )
    Payment.objects.create(
        user=buyer,  # BUYER purchased
        post=post,
        stripe_checkout_id="cs_1",
        amount=5,
        currency="usd",
        paid=True,
    )

    url = reverse("payments:create_checkout_session", args=[post.id])
    response = client.post(url)

    assert response.status_code == 200
    assert "Already purchased" in response.data["message"]


# --- Webhook tests ---


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_success(mock_construct_event, client):
    user = User.objects.create_user(username="buyer", password="pass")
    post = BlogPost.objects.create(
        title="Premium", body="Body", author=user, premium=True
    )
    payment = Payment.objects.create(
        user=user,
        post=post,
        stripe_checkout_id="cs_test_1",
        amount=5,
        currency="usd",
        status="pending",
    )

    mock_construct_event.return_value = {
        "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_test_1", "payment_intent": "pi_test_123"}},
    }

    response = client.post(
        reverse("payments:stripe_webhook"),
        data={},
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="fake_signature",
    )

    payment.refresh_from_db()
    assert response.status_code == 200
    assert payment.status == "completed"
    assert payment.paid is True


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_webhook_signature_error(mock_construct_event, client):
    mock_construct_event.side_effect = stripe.SignatureVerificationError(
        "Invalid signature", sig_header="wrong"
    )

    response = client.post(
        reverse("payments:stripe_webhook"),
        data={},
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="wrong",
    )

    assert response.status_code == 400
