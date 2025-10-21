from django.urls import path
from payments import views, webhooks

app_name = "payments"  # for defining namespace

urlpatterns = [
    path(
        "create-checkout-session/<int:post_id>/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("stripe/webhook/", webhooks.stripe_webhook, name="stripe_webhook"),
]
