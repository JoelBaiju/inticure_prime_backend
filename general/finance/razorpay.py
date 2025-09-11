import razorpay
from django.conf import settings
from general.models import PreTransactionData
from razorpay.errors import SignatureVerificationError



# Initialize client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
def initiate_razorpay_payment(pretransaction_id,appointment_id):
    # Get transaction details
    try:
        transaction = PreTransactionData.objects.get(pretransaction_id=pretransaction_id)
    except PreTransactionData.DoesNotExist:
        return {"error": "Invalid pretransaction_id"}

    user_id = transaction.customer.id  # Assuming transaction is linked to a user

    # Create Razorpay order
    try:
        razorpay_order = razorpay_client.order.create({
            'amount': int(transaction.total_amount * 100),
            'currency': transaction.currency,
            'receipt': str(pretransaction_id),
            'payment_capture': "1",
            'notes': {
                'pretransaction_id': str(pretransaction_id),
                'appointment_id': str(appointment_id),
            }
        })

    except Exception as e:
        return {"error": str(e)}
    transaction.razorpay_order_id = razorpay_order['id']
    transaction.save()  # Save the order ID to the transaction

    # Prepare and return payment data
    return {
        'key': settings.RAZORPAY_API_KEY,
        'amount': int(transaction.total_amount * 100),
        'currency': transaction.currency,
        'order_id': razorpay_order['id'],
        'pretransaction_id': pretransaction_id,
        'user_id': user_id,
        "payment_gateway":'razor_pay'
    }
















from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
import razorpay
from analysis.views import ConfirmAppointment
@csrf_exempt
def verify_payment(request):
    if request.method != "POST":
        print("❌ Invalid request method:", request.method)
        return JsonResponse({"error": "Invalid request method"}, status=400)

    # Validate webhook secret exists
    webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', None)
    if not webhook_secret:
        print("❌ Razorpay webhook secret not configured")
        return JsonResponse({"error": "Server configuration error"}, status=500)

    # Validate signature header exists
    received_signature = request.headers.get('X-Razorpay-Signature')
    if not received_signature:
        print("❌ Missing X-Razorpay-Signature header")
        return JsonResponse({"error": "Missing signature header"}, status=400)

    # Validate request body exists
    try:
        request_body = request.body
        if not request_body:
            print("❌ Empty request body")
            return JsonResponse({"error": "Empty request body"}, status=400)
            
        request_body = request_body.decode('utf-8')
    except UnicodeDecodeError as e:
        print(f"❌ UnicodeDecodeError: {str(e)}")
        return JsonResponse({"error": "Invalid request body encoding"}, status=400)
    except Exception as e:
        print(f"❌ Unexpected error decoding request body: {type(e).__name__}: {str(e)}")
        return JsonResponse({"error": "Invalid request body"}, status=400)

    # Verify signature
    try:
        razorpay_client.utility.verify_webhook_signature(
            request_body,
            received_signature,
            webhook_secret
        )
        print("✅ Signature verified")
        # Continue with payment processing...
        
    except razorpay.errors.SignatureVerificationError as e:
        print(f"❌ SignatureVerificationError: {str(e)}")
        return JsonResponse({"status": "failed", "message": "Signature verification failed"}, status=400)
    except Exception as e:
        print(f"❌ Error during verification: {type(e).__name__}: {str(e)}")
        return JsonResponse({"status": "failed", "message": "Error during verification"}, status=400)
    try:
        data = json.loads(request_body)
        event = data.get("event")

        if event == "payment.captured" or event == "order.paid":
            payment_entity = data['payload']['payment']['entity']
            payment_id = payment_entity['id']  # <-- Razorpay payment_id
            notes = data['payload']['payment']['entity'].get('notes', {})
            pretransaction_id = notes.get('pretransaction_id')
            appointment_id = notes.get('appointment_id')
            pretransation = PreTransactionData.objects.get(pretransaction_id=pretransaction_id)
            RazorpayTransaction.objects.create(
                pretransaction=pretransation,
                razorpay_payment_id=payment_id,
            )
            ConfirmAppointment(pretransaction_id=pretransaction_id, appointment_id=appointment_id)
            print(f"✅ Payment captured: {pretransaction_id}, Amount: {appointment_id}")
            
        elif event == "payment.authorized":
            print("🕓 Payment authorized, awaiting capture...")

        elif event == "payment.failed":
            print("❌ Payment failed")

        else:
            print(f"⚠️ Unhandled event type: {event}")

        return JsonResponse({"status": "success", "event": event})

    except json.JSONDecodeError as e:
        print(f"❌ JSONDecodeError: {str(e)}")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except KeyError as e:
        print(f"❌ KeyError: {str(e)}")
        return JsonResponse({"error": f"Missing key in payload: {str(e)}"}, status=400)
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
    













from general.models import PreTransactionData, RazorpayTransaction  # Example model storing Razorpay payment IDs
from customer.models import  Refund

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

def process_razorpay_refund(pretransaction_id, amount=None):
    try:
        transaction = PreTransactionData.objects.get(pretransaction_id=pretransaction_id)
    except PreTransactionData.DoesNotExist:
        return {"error": "Invalid pretransaction_id"}

    try:
        # Find stored Razorpay payment ID (must have saved it after payment success)
        razorpay_txn = RazorpayTransaction.objects.filter(
            pretransaction_id=pretransaction_id
        ).first()

        if not razorpay_txn or not razorpay_txn.payment_id:
            return {"error": "No valid Razorpay transaction found"}

        # Prepare refund parameters
        refund_params = {}
        if amount:
            refund_params["amount"] = int(amount * 100)  # Razorpay expects amount in paise

        # Create refund
        refund = razorpay_client.payment.refund(
            razorpay_txn.razorpay_payment_id,
            refund_params
        )

        refund_obj = Refund.objects.filter(
            appointment=transaction.appointment,

        ).first()
        refund_obj.refund_status = refund.get('status', 'failed')
        refund_obj.razorpay_refund_id = refund.get('id')

        print(f"✅ Refund successful for {pretransaction_id}")
        print(f"Refund ID: {refund.get('id')}")
        print(f"Refund Status: {refund.get('status')}")

        return {
            "status": "success",
            "message": "Refund processed successfully"
        }

    except razorpay.errors.BadRequestError as e:
        print(f"❌ Razorpay BadRequestError: {str(e)}")
        return {"error": "Refund request invalid"}
    except razorpay.errors.ServerError as e:
        print(f"❌ Razorpay ServerError: {str(e)}")
        return {"error": "Razorpay server error"}
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {"error": "Something went wrong while processing refund"}
