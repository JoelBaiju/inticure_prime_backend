import stripe
from django.conf import settings
from general.models import PreTransactionData
from django.contrib.auth import get_user_model

User = get_user_model()

stripe.api_key = settings.STRIPE_SECRET_KEY
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
    customer = transaction.customer

  
    stripe_customer_id = customer.stripe_customer_id

    if not stripe_customer_id:
        created_customer = stripe.Customer.create(
            email=customer.email,
            name=f"{customer.user.first_name} {customer.user.last_name}",
            metadata={"user_id":customer.id }
        )

        # Save in our DB
        customer.stripe_customer_id = created_customer.id
        customer.save()
        stripe_customer_id = created_customer.id

    # Step 2: Create PaymentIntent with the customer attached
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=stripe_customer_id,
            metadata={
                'pretransaction_id': pretransaction_id,
                'user_id': customer.id
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
    customer = transaction.customer

    # Step 1: Get or create Stripe Customer
    stripe_customer_id = getattr(customer, "stripe_customer_id", None)

    if not stripe_customer_id:
        created_customer = stripe.Customer.create(
            email=customer.email,
            name=f"{customer.user.first_name} {customer.user.last_name}",
            metadata={"user_id": customer.id}
        )
        # Save in DB
        customer.stripe_customer_id = created_customer.id
        customer.save()
        stripe_customer_id = created_customer.id

    # Step 2: Create checkout session with customer attached
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer=stripe_customer_id,
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
            billing_address_collection="required",  

        )

        return {
            "payment_url": session.url,
            "pretransaction_id": pretransaction_id,
            "payment_gateway": "stripe",
            "amount": amount,
            "currency": Countries.objects.get(currency=transaction.currency).currency_symbol
        }

    except Exception as e:
        return {"error": str(e)}





from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import stripe
import json
from analysis.views import ConfirmAppointment
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import stripe
import json
from analysis.views import ConfirmAppointment
from django.conf import settings
from general.models import PreTransactionData, StripeTransactions

@csrf_exempt
def verify_payment_stripe(request):
    if request.method != "POST":
        print('invalid request method')



    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    if not endpoint_secret:
        print('endpoint_secret not found')

    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    if not sig_header:
        print('sig_header not found')

    payload = request.body
    if not payload:
        print('payload not found')

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret
        )
    except stripe.error.SignatureVerificationError:
        print('Signature verification failed')
    except Exception:
        print('Error during verification')

    obj = event['data']['object']
    event_type = event.get('type', "")
    metadata = obj.get('metadata', {})

    try:
        if event_type in ["checkout.session.completed", "payment_intent.succeeded"]:
            pretransaction_id = metadata.get('pretransaction_id')
            appointment_id = metadata.get('appointment_id')

            # Call your appointment confirmation logic
            print("pre and app " , pretransaction_id , appointment_id)
            if pretransaction_id and appointment_id:
                print('inside the condition')
                ConfirmAppointment(pretransaction_id=pretransaction_id, appointment_id=appointment_id)

            # Save payment_intent_id if needed
            payment_intent_id = (
                obj.get("id") if event_type == "payment_intent.succeeded"
                else obj.get("payment_intent")
            )
            if pretransaction_id:
                # Save the transaction in your model
                print(pretransaction_id)
                pretransaction = PreTransactionData.objects.get(pretransaction_id=pretransaction_id)
                StripeTransactions.objects.create(
                    pretransaction=pretransaction,
                    stripe_payment_intent_id=payment_intent_id
                )
            print('success')

            return JsonResponse({
                "status": "success",
                "event": event_type,
                "metadata": metadata,
                "payment_intent_id": payment_intent_id
            })

        elif event_type == "payment_intent.payment_failed":
            print('payment_intent.payment_failed')
            return JsonResponse({"status": "failed", "event": event_type, "metadata": metadata})

        elif event_type in [
            "checkout.session.async_payment_failed",
            "checkout.session.expired",
            "payment_intent.canceled"
        ]:
            print('payment_intent.canceled')

            return JsonResponse({"status": "failed", "event": event_type, "metadata": metadata})

        elif event_type in [
            "checkout.session.async_payment_succeeded",
            "payment_link.created",
            "payment_link.updated",
            "payment_intent.created"
        ]:
            print('payment_intent.created')

            return JsonResponse({"status": "info", "event": event_type, "metadata": metadata})

        else:
            print('unhandled')

            return JsonResponse({"status": "unhandled", "event": event_type, "metadata": metadata})

    except Exception as e:
        print('error', str(e))


        return JsonResponse({"error": str(e)}, status=500)










from customer.models import  Refund



def process_stripe_refund(pretransaction_id, amount=None):
    try:
        transaction = PreTransactionData.objects.get(pretransaction_id=pretransaction_id)
    except PreTransactionData.DoesNotExist:
        return {"error": "Invalid pretransaction_id"}

    try:
        # Get the related Stripe transaction record
        stripe_txn = StripeTransactions.objects.filter(
            pretransaction=transaction, stripe_payment_intent_id__isnull=False
        ).first()

        if not stripe_txn or not stripe_txn.stripe_payment_intent_id:
            return {"error": "No valid Stripe transaction found"}

        # Fetch PaymentIntent to get charge ID
        payment_intent = stripe.PaymentIntent.retrieve(stripe_txn.stripe_payment_intent_id)
        charge_id = payment_intent.charges.data[0].id

        # Amount in cents (if partial refund)
        refund_params = {"charge": charge_id}
        if amount:
            refund_params["amount"] = int(amount * 100)  # Convert to smallest currency unit

        # Create refund
        refund = stripe.Refund.create(**refund_params)
        refund_record = Refund.objects.filter(appointment=transaction.appointment).first()
        if not refund_record:
            return {"error": "No related refund record found"}
        refund_record.stripe_refund_id = refund.id
        refund_record.refund_status = refund.status
        refund_record.save()

        print(f"✅ Refund successful for {pretransaction_id}")
        print(f"Refund ID: {refund.id}")
        print(f"Refund Status: {refund.status}")

        return {
            "status": "success",
            "message": "Refund processed successfully"
        }

    except stripe.error.StripeError as e:
        print(f"❌ Stripe API error: {str(e)}")
        return {"error": "Unable to process refund"}
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {"error": "Something went wrong while processing refund"}
