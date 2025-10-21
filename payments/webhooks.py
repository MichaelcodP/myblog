from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
import logging

from payments.models import Payment

logger = logging.getLogger(__name__)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.error(f"Webhook error: {e}")
        return HttpResponse(status=400)

    def handle_successful_payment(session):
        payment = Payment.objects.filter(stripe_checkout_id=session.get("id")).first()
        if payment:
            payment.status = "completed"
            payment.payment_intent_id = session.get("payment_intent")
            payment.paid = True
            payment.save()
            logger.info(
                f"Payment successful for user {payment.user} and post {payment.post.id}"
            )
        else:
            logger.warning(f"No payment record found for session {session.get("id")}")

    def handle_failed_payment(session):
        payment = Payment.objects.filter(stripe_checkout_id=session.get("id")).first()
        if payment:
            payment.status = "failed"
            payment.save()
            logger.warning(
                f"Payment failed for user {payment.user} and post {payment.post.id}"
            )

    try:
        if event["type"] == "checkout.session.completed":
            handle_successful_payment(event["data"]["object"])
        elif event["type"] == "payment_intent.payment_failed":
            handle_failed_payment(event["data"]["object"])
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return HttpResponse(status=400)
