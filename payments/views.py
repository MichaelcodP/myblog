from decimal import Decimal
from django.conf import settings
from django.urls import reverse
import stripe
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from blog.models import BlogPost
from payments.models import Payment

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    method="get",
    operation_description="Handle successful payment callback",
    operation_summary="Payment Success Handler",
    responses={
        200: openapi.Response(
            description="Success response",
            examples={
                "application/json": {
                    "status": "success",
                    "message": "Payment completed successfully",
                    "next": "/api/posts/",
                }
            },
        )
    },
    tags=["payments"],
)
@api_view(["GET", "POST"])
def payment_success(request):
    """Handle successful payment callback."""

    if request.user.is_authenticated:
        recent_payment = (
            Payment.objects.filter(user=request.user, status="pending")
            .order_by("-created_at")
            .first()
        )

        if recent_payment:
            recent_payment.status = "completed"
            recent_payment.paid = True
            recent_payment.save()

    if request.accepted_renderer.format == "html":
        messages.success(
            request,
            "Payment completed successfully! You now have access to the content.",
        )
        return redirect("home")

    return Response(
        {
            "status": "success",
            "message": "Payment completed successfully",
            "next": request.build_absolute_uri("/api/posts/"),
        }
    )


@swagger_auto_schema(
    method="get",
    operation_description="Handle cancelled payment callback",
    operation_summary="Payment Cancel Handler",
    responses={
        200: openapi.Response(
            description="Cancel response",
            examples={
                "application/json": {
                    "status": "cancelled",
                    "message": "Payment was cancelled by the user",
                    "next": "/api/posts/",
                }
            },
        )
    },
    tags=["payments"],
)
@api_view(["GET"])
def payment_cancel(request):
    """Handle cancelled payment callback from Stripe."""
    if request.accepted_renderer.format == "html":
        messages.info(request, "Payment was cancelled. You can try again later.")
        return redirect("home")

    return Response(
        {
            "status": "cancelled",
            "message": "Payment was cancelled by the user",
            "next": request.build_absolute_uri("/api/posts/"),
        }
    )


@swagger_auto_schema(
    method="post",
    operation_description="Create a Stripe checkout session for premium content",
    operation_summary="Create Checkout Session",
    manual_parameters=[
        openapi.Parameter(
            "post_id",
            openapi.IN_PATH,
            description="ID of the premium post to purchase",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Checkout session created",
            examples={"application/json": {"id": "cs_test_..."}},
        ),
        400: "Invalid request or post is not premium",
        401: "Authentication required",
        404: "Post not found",
    },
    security=[{"Bearer": []}],
    tags=["payments"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request, post_id):
    """Create a Stripe checkout session for purchasing premium content."""
    post = get_object_or_404(BlogPost, pk=post_id)

    amount = Decimal(settings.STRIPE_PRICE_AMOUNT)
    currency = settings.STRIPE_CURRENCY

    if not post.premium:
        return Response({"error": "This post is not premium."}, status=400)

    if post.author == request.user:
        return Response({"message": "Authors can access their posts for free."})

    # Check for existing payment FIRST
    existing_payment = Payment.objects.filter(user=request.user, post=post).first()
    if existing_payment:
        if existing_payment.paid or existing_payment.status == "completed":
            return Response({"message": "Already purchased."})
        # If pending payment exists, delete it and create new one
        existing_payment.delete()

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": post.title},
                    "unit_amount": int(amount * Decimal("100")),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(reverse("payments:payment_success")),
        cancel_url=request.build_absolute_uri(reverse("payments:payment_cancel")),
        metadata={"user_id": request.user.id, "post_id": post.id},
    )

    Payment.objects.create(
        user=request.user,
        post=post,
        stripe_checkout_id=checkout_session.id,
        amount=amount,
        currency=currency,
        status="pending",
    )

    return Response({"id": checkout_session.id})


def payment_demo(request, post_id):
    """Demo page showing complete Stripe checkout flow"""
    post = get_object_or_404(BlogPost, id=post_id)

    if not post.premium:
        return Response({"error": "This post is not premium"}, status=400)

    # Check if user already paid
    has_paid = False
    if request.user.is_authenticated:
        has_paid = Payment.objects.filter(
            user=request.user, post=post, status="completed"
        ).exists()

    context = {
        "post": post,
        "stripe_publishable_key": getattr(
            settings, "STRIPE_PUBLISHABLE_KEY", "pk_test_demo"
        ),
        "post_id": post_id,
        "has_paid": has_paid,
        "is_author": (
            request.user == post.author if request.user.is_authenticated else False
        ),
    }
    return render(request, "payments/demo.html", context)
