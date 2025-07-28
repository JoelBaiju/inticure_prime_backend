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

@csrf_exempt
def verify_payment_stripe(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'status': 'failed', 'message': 'Signature verification failed'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    # Handle the event
    if event['type'] == 'checkout.session.async_payment_failed':
      session = event['data']['object']
      print("Payment Failed:", session)
    elif event['type'] == 'checkout.session.async_payment_succeeded':
      session = event['data']['object']
      print("Payment Succeeded:", session)
    elif event['type'] == 'checkout.session.completed':
      session = event['data']['object']
      print("Payment Completed:", session)
    elif event['type'] == 'checkout.session.expired':
      session = event['data']['object']
      print("Payment Expired:", session)
    elif event['type'] == 'payment_intent.canceled':
      payment_intent = event['data']['object']
      print("Payment Canceled:", payment_intent)
    elif event['type'] == 'payment_intent.created':
      payment_intent = event['data']['object']
      print("Payment Created:", payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
      payment_intent = event['data']['object']
      print("Payment Failed:", payment_intent)
    elif event['type'] == 'payment_intent.succeeded':
      payment_intent = event['data']['object']
      print("Payment Succeeded:", payment_intent)
    elif event['type'] == 'payment_link.created':
      payment_link = event['data']['object']
      print("Payment Link Created:", payment_link)
    elif event['type'] == 'payment_link.updated':
      payment_link = event['data']['object']
      print("Payment Link Updated:", payment_link)
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    