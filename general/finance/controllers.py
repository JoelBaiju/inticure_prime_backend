from administrator.models import Countries
from analysis.models import AppointmentHeader
from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated
from .razorpay import initiate_razorpay_payment
from general.models import PreTransactionData
from .calculators import first_consultation_cost_calculator

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .stripe import initiate_stripe_payment , initiate_stripe_payment_link
import logging
logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def initiate_payment_controller(request):
    """
    Initiate payment for an appointment.
    based on the country and currency of the user.
    uses razorpay for indian users and stripe for international users.
    """
    appointment_id = request.query_params.get('appointment_id')
         
    if not appointment_id:
        return Response({"error": "Appointment ID is required"}, status=400)
    appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
    if not appointment:
        return Response({"error": "Appointment not found"}, status=404)
    if appointment.is_couple:
        if not appointment.customer.partner:
            return Response({"error": "Partner details are required for couple appointments"}, status=400)
    country = appointment.customer.country_details 
    
    if appointment.doctor.is_prescription_allowed:
        logger.debug("yeah got into doctor presatioprtion allowed")
        country = Countries.objects.filter(country_name = 'India').first()
        cost_obj    = first_consultation_cost_calculator(appointment_id,country)   
    else:
        cost_obj    = first_consultation_cost_calculator(appointment_id)   

    

    if country.representation == "IN" and appointment.customer.country_details.representation=="IN":
        temp_trans_obj  =   PreTransactionData.objects.create(
            customer    =   appointment.customer,
            appointment =   appointment,
            total_amount=   cost_obj['total_cost'],
            vendor_fee  =   cost_obj['platform_fee'],
            tax         =   0,
            currency    =   country.currency,
            gateway     =   "razorpay",
        )
        payment_obj = initiate_razorpay_payment(pretransaction_id=temp_trans_obj.pretransaction_id , appointment_id=appointment_id)
        if 'error' in payment_obj:
            logger.error(f"Error initiating Razorpay payment: {payment_obj['error']}")
            return Response({"error": payment_obj['error']}, status=400)
        
    else:
        temp_trans_obj = PreTransactionData.objects.create(
            customer=appointment.customer,
            appointment=appointment,
            total_amount=cost_obj['total_cost'],
            vendor_fee=cost_obj['platform_fee'],
            tax=0,
            currency=country.currency,
            gateway="stripe",
        )
        payment_obj = initiate_stripe_payment_link(pretransaction_id=temp_trans_obj.pretransaction_id , appointment_id=appointment_id)
    if 'error' in payment_obj:
        logger.error(f"Error initiating Stripe payment: {payment_obj['error']}")
        return Response({"error": payment_obj['error']}, status=400)
        



    return Response(payment_obj, status=200)

    


from general.finance.stripe import process_stripe_refund
from general.finance.razorpay import process_razorpay_refund

def refund_controller(pretransaction_id):
    """
    Controller to handle refund requests.
    It processes the refund based on the pretransaction_id and amount.
    """

    if not pretransaction_id:
        return {"error": "Pretransaction ID is required"}
    try:
        transaction = PreTransactionData.objects.get(pretransaction_id=pretransaction_id)
        if transaction.gateway == "razor_pay":
            result = process_razorpay_refund(pretransaction_id, transaction.total_amount)
        elif transaction.gateway == "stripe":
            result = process_stripe_refund(pretransaction_id, transaction.total_amount)
        else:
            return {"error": "Unsupported payment gateway"}
        return result
    except PreTransactionData.DoesNotExist:
        return {"error": "Pretransaction not found"}
    




# @csrf_exempt
# def create_stripe_checkout(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request method"}, status=400)

#     try:
#         data = json.loads(request.body)
#         pretransaction_id = data.get('pretransaction_id') 
#         result = initiate_stripe_payment(pretransaction_id)
#         return JsonResponse(result)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)



