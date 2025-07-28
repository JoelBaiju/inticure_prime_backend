from analysis.models import AppointmentHeader
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .razorpay import initiate_razorpay_payment
from general.models import PreTransactionData
from .calculators import first_consultation_cost_calculator

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .stripe import initiate_stripe_payment , initiate_stripe_payment_link



@api_view(['GET'])
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
    
    country = appointment.customer.country_details 
    cost_obj    = first_consultation_cost_calculator(appointment_id)   


    if country.representation == "IN" :
        temp_trans_obj = PreTransactionData.objects.create(
            customer=appointment.customer,
            appointment=appointment,
            total_amount=cost_obj['total_cost'],
            vendor_fee=cost_obj['platform_fee'],
            tax=0,
            currency=country.currency,
            gateway="razorpay",
        )
        payment_obj = initiate_razorpay_payment(pretransaction_id=temp_trans_obj.pretransaction_id , appointment_id=appointment_id)
        if 'error' in payment_obj:
            return Response({"error": payment_obj['error']}, status=400)
        
    else:
        temp_trans_obj = PreTransactionData.objects.create(
            customer=appointment.customer,
            appointment=appointment,
            total_amount=cost_obj['total_cost'],
            vendor_fee=cost_obj['platform_fee'],
            tax=0,
            currency=appointment.customer.country_details.currency,
            gateway="stripe",
        )
        payment_obj = initiate_stripe_payment_link(pretransaction_id=temp_trans_obj.pretransaction_id , appointment_id=appointment_id)
    if 'error' in payment_obj:
        return Response({"error": payment_obj['error']}, status=400)
        



    return Response(payment_obj, status=200)

    









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



