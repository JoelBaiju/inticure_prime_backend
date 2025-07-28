from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from administrator.models import PaymentEntries
from analysis.models import AppointmentHeader

# def consultation_cost_details_view(request):
#     entry = None
#     appointment_id = None

#     if request.method == 'POST':
#         appointment_id = request.POST.get('appointment_id')

#         try:
#             # Get the related appointment
#             entry = PaymentEntries.objects.get(appointment__appointment_id=appointment_id)
#         except PaymentEntries.DoesNotExist:
#             entry = None

#     return render(request, 'consultation_cost_details.html', {
#         'entry': entry,
#         'appointment_id': appointment_id
#     })



def consultation_cost_details_view(request):
 

    return render(request, 'price_calculator.html')
