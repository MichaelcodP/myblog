from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings

from payments.models import Payment


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        checkout_id = session.get("id")

        payment = Payment.objects.filter(stripe_checkout_id=checkout_id).first()
        if payment:
            payment.paid = True
            payment.save()

    return HttpResponse(status=200)
