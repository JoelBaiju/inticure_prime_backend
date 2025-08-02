import stripe
from django.conf import settings
from general.models import PreTransactionData
from django.contrib.auth import get_user_model

User = get_user_model()

stripe.api_key = settings.STRIPE_SECRET_KEY

def initiate_stripe_payment(pretransaction_id):

    try:
        transaction = PreTransactionData.objects.get(pretransaction_id=pretransaction_id)
    except PreTransactionData.DoesNotExist:
        return {"error": "Invalid pretransaction_id"}

    amount = int(transaction.total_amount * 100)  # Convert to smallest currency unit
    currency = transaction.currency.lower()
    

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={
                'pretransaction_id': pretransaction_id,
                'user_id': transaction.customer.id
            },
            automatic_payment_methods={'enabled': True}
        )
        return {
            "client_secret": intent.client_secret,
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "pretransaction_id": pretransaction_id
        }

    except Exception as e:
        return {"error": str(e)}












from administrator.models import Countries
import stripe
from django.conf import settings
from general.models import PreTransactionData
from django.contrib.auth import get_user_model

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

def initiate_stripe_payment_link(pretransaction_id, appointment_id):
    try:
        transaction = PreTransactionData.objects.get(pretransaction_id=pretransaction_id)
    except PreTransactionData.DoesNotExist:
        return {"error": "Invalid pretransaction_id"}

    amount = int(transaction.total_amount * 100)  # in smallest currency unit
    currency = transaction.currency.lower()

    try:
        # Create the checkout session with redirect URLs
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': f"Payment for Appointment {appointment_id}"
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            metadata={
                'pretransaction_id': pretransaction_id,
                'appointment_id': str(appointment_id),
            },
            success_url=f"{settings.FRONT_END_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}",
            # cancel_url=f"{settings.FRONT_END_FAILIURE_URL}",
        )

        # Optionally store session URL in DB
        # transaction.stripe_payment_link = session.url
        # transaction.save()

        return {
            "payment_url": session.url,
            "pretransaction_id": pretransaction_id,
            "payment_gateway": "stripe",
            "amount": amount,
            "currency":Countries.objects.get(currency = transaction.currency).currency_symbol
        }

    except Exception as e:
        return {"error": str(e)}







from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import stripe
import json
from analysis.views import ConfirmAppointment


@csrf_exempt
def verify_payment_stripe(request):
    if request.method != "POST":
        print("❌ Invalid request method:", request.method)
        return JsonResponse({"error": "Invalid request method"}, status=400)

    # Validate Stripe secret key
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    if not endpoint_secret:
        print("❌ Stripe endpoint secret not configured")
        return JsonResponse({"error": "Server configuration error"}, status=500)

    # Validate signature header
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    if not sig_header:
        print("❌ Missing Stripe signature header")
        return JsonResponse({"error": "Missing signature header"}, status=400)

    # Validate request body
    try:
        payload = request.body
        if not payload:
            print("❌ Empty request body")
            return JsonResponse({"error": "Empty request body"}, status=400)
    except Exception as e:
        print(f"❌ Error reading request body: {type(e).__name__}: {str(e)}")
        return JsonResponse({"error": "Invalid request body"}, status=400)

    # Verify Stripe webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret
        )
        print("✅ Stripe signature verified")
    except stripe.error.SignatureVerificationError as e:
        print(f"❌ SignatureVerificationError: {str(e)}")
        return JsonResponse({'status': 'failed', 'message': 'Signature verification failed'}, status=400)
    except Exception as e:
        print(f"❌ Error during verification: {type(e).__name__}: {str(e)}")
        return JsonResponse({'status': 'failed', 'message': 'Error during verification'}, status=400)

    # Parse JSON body
    try:
        event_data = json.loads(payload.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"❌ JSONDecodeError: {str(e)}")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Handle events
    event_type = event.get('type')
    obj = event['data']['object']

    try:
        if event_type in ["checkout.session.completed", "payment_intent.succeeded"]:
            metadata = obj.get('metadata', {})
            pretransaction_id = metadata.get('pretransaction_id')
            appointment_id = metadata.get('appointment_id')

            ConfirmAppointment(pretransaction_id=pretransaction_id, appointment_id=appointment_id)
            print(f"✅ Payment successful: {pretransaction_id}, Appointment: {appointment_id}")

        elif event_type == "payment_intent.payment_failed":
            print("❌ Payment failed:", obj)

        elif event_type == "checkout.session.async_payment_failed":
            print("❌ Async payment failed:", obj)

        elif event_type == "checkout.session.async_payment_succeeded":
            print("✅ Async payment succeeded:", obj)

        elif event_type == "checkout.session.expired":
            print("⌛ Session expired:", obj)

        elif event_type == "payment_intent.canceled":
            print("🚫 Payment canceled:", obj)

        elif event_type == "payment_intent.created":
            print("ℹ️ Payment intent created:", obj)

        elif event_type == "payment_link.created":
            print("🔗 Payment link created:", obj)

        elif event_type == "payment_link.updated":
            print("🔄 Payment link updated:", obj)

        else:
            print(f"⚠️ Unhandled event type: {event_type}")

        return JsonResponse({"status": "success", "event": event_type})

    except KeyError as e:
        print(f"❌ KeyError: {str(e)}")
        return JsonResponse({"error": f"Missing key in payload: {str(e)}"}, status=400)
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
