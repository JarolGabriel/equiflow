import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StripePayment

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    """
    API View to create a Stripe PaymentIntent.
    This provides a client_secret to the frontend to complete the payment.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # We assume for now a fixed price for "Pro Plan" (e.g., $29.99)
            # You can also get this from request.data if prices are dynamic
            amount = 2999  # $29.99 in cents
            currency = "usd"

            # 1. Create the PaymentIntent in Stripe
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata={"user_id": str(request.user.id), "email": request.user.email},
            )

            # 2. Save the transaction as PENDING in our PostgreSQL
            StripePayment.objects.create(
                user=request.user,
                stripe_id=intent.id,
                amount=amount / 100,  # Convert back to decimal for our DB
                currency=currency,
                status=StripePayment.PaymentStatus.PENDING,
            )

            # 3. Return the client_secret to the (future) frontend
            return Response(
                {"clientSecret": intent.client_secret, "paymentIntentId": intent.id},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    """
    Webhook view to handle Stripe events.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Manejar el evento de pago exitoso
        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            stripe_id = intent["id"]

            # Buscamos el pago en nuestra DB y lo completamos
            try:
                payment = StripePayment.objects.get(stripe_id=stripe_id)
                payment.status = StripePayment.PaymentStatus.COMPLETED
                payment.save()

                # ACTUALIZAMOS AL USUARIO A PRO
                user = payment.user
                user.is_pro = True
                user.save()

                print(
                    f"💰 Payment Succeeded: {stripe_id} - User {user.email} is now PRO"
                )
            except StripePayment.DoesNotExist:
                print(f"⚠️ Payment {stripe_id} not found in DB")

        return HttpResponse(status=200)
