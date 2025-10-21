from decimal import Decimal
from django.conf import settings
import stripe
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from blog.models import BlogPost
from payments.models import Payment


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)

    amount = Decimal(settings.STRIPE_PRICE_AMOUNT)
    currency = settings.STRIPE_CURRENCY

    if not post.premium:
        return Response({"error": "This post is not premium."}, status=400)

    if post.author == request.user:
        return Response({"message": "Authors can access their posts for free."})

    # Avoid duplicate payments
    if Payment.objects.filter(user=request.user, post=post, paid=True).exists():
        return Response({"message": "Already purchased."})

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": post.title},
                    "unit_amount": int(amount * 100),  # cent convertion
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri("/payment/success"),
        cancel_url=request.build_absolute_uri("/payment/cancel"),
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
