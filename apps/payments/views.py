import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StripePayment

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Create Stripe Payment Intent",
        description="Starts the payment process for the PRO Plan ($29.99). Returns a `clientSecret` that the frontend uses to securely collect payment details.",
        responses={201: dict},
    )
    def post(self, request, *args, **kwargs):
        try:
            amount = 2999  # $29.99 in cents
            currency = "usd"

            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata={"user_id": str(request.user.id), "email": request.user.email},
            )

            StripePayment.objects.create(
                user=request.user,
                stripe_id=intent.id,
                amount=amount / 100,
                currency=currency,
                status=StripePayment.PaymentStatus.PENDING,
            )

            return Response(
                {"clientSecret": intent.client_secret, "paymentIntentId": intent.id},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Stripe Webhook Handler",
        description="Internal endpoint to receive events from Stripe. It automatically upgrades the user to PRO when a payment succeeds.",
        exclude=True,
    )
    def post(self, request, *args, **kwargs):
        # ... (Tu código de webhook se mantiene exactamente igual) ...
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            stripe_id = intent["id"]

            try:
                payment = StripePayment.objects.get(stripe_id=stripe_id)
                payment.status = StripePayment.PaymentStatus.COMPLETED
                payment.save()

                user = payment.user
                user.is_pro = True
                user.save()

                print(f"Payment Succeeded: {stripe_id} - User {user.email} is now PRO")
            except StripePayment.DoesNotExist:
                print(f" Payment {stripe_id} not found in DB")

        return HttpResponse(status=200)
