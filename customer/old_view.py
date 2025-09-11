# from pydoc import doc
# from tracemalloc import start
# from django.shortcuts import render
# from rest_framework import generics
# from .models import *
# from django.contrib.auth.models import User
# from general.models import *
# from general.utils import *
# from general.twilio import *
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from customer.serializers import CustomerProfileSerializer, CustomerDashboardSerializer

# from analysis.models import AppointmentHeader


# class CustomerDashboard(generics.RetrieveAPIView):
#     permission_classes = [IsAuthenticated]
#     """
#     API to get customer dashboard details
#     """
#     serializer_class = CustomerDashboardSerializer

#     def get(self, request, *args, **kwargs):
#         customer_profile = CustomerProfile.objects.get(user=self.request.user)
#         serializer = self.get_serializer(customer_profile)
        
#         appointments = AppointmentHeader.objects.filter(customer=customer_profile).order_by('-start_time')
#         return Response(serializer.data)
    


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Q
# from datetime import datetime, timedelta
# from doctor.models import DoctorAppointment
# from django.utils import  timezone



# from doctor.slots_service import get_available_slots










# # class DoctorAvailabilityView(APIView):
# #     def get(self, request):
# #         doctor_id = request.query_params.get("doctor_id")
# #         date_str = request.query_params.get("date")  # Optional
# #         is_couple = request.query_params.get("is_couple", "false").lower() == "true"

# #         if not doctor_id:
# #             return Response({"error": "doctor_id is required."}, status=status.HTTP_400_BAD_REQUEST)

# #         try:
# #             doctor_id = int(doctor_id)
# #         except ValueError:
# #             return Response({"error": "doctor_id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        
# #         if date_str:
# #             try:
# #                 # Convert the date string to UTC datetime and extract the date component
# #                 from general.utils import parse_datetime_to_utc
# #                 # Append time to make it a complete datetime string
# #                 datetime_str = f"{date_str}T00:00:00"
# #                 utc_datetime = parse_datetime_to_utc(datetime_str, "%Y-%m-%dT%H:%M:%S", request.user)
# #                 date_obj = utc_datetime.date()
# #                 print(date_obj)
# #             except ValueError:
# #                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
# #         else:
# #             date_obj = timezone.now().date() + timedelta(days=1)

# #         results = get_available_slots(doctor_id=doctor_id, date=date_obj, is_couple=is_couple)

# #         # Format slots to match your frontend's expected format
# #         print(timezone.now().date())
# #         print(date_obj)
# #         results['current_date']=str(date_obj)
# #         return Response({
# #             "available_slots": results,
# #         }, status=status.HTTP_200_OK)
    




# from general.utils import get_customer_timezone

# class DoctorAvailabilityView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         doctor_id = request.query_params.get("doctor_id")
#         date_str = request.query_params.get("date")  # Optional
#         is_couple = request.query_params.get("is_couple", "false").lower() == "true"

#         if not doctor_id:
#             return Response({"error": "doctor_id is required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             doctor_id = int(doctor_id)
#         except ValueError:
#             return Response({"error": "doctor_id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

#         # Get doctor's timezone
#         timeZone = get_customer_timezone(request.user)
#         print(" timezone:", timeZone)
#         if not timeZone:
#             return Response({"error": "Doctor time zone not set"}, status=400)

#         # Get base and end date in doctor's timezone
#         base_date, end_of_base_date = get_current_time_in_utc_from_tz(timeZone)
#         base_date += timedelta(days=1)  # tomorrow
#         end_of_base_date += timedelta(days=1)

#         if date_str:
#             try:
#                 preferred_dt_start = convert_local_dt_to_utc(
#                     f"{date_str}T00:00:00",
#                     timeZone
#                 )
#                 preferred_dt_end = convert_local_dt_to_utc(
#                     f"{date_str}T23:59:59",
#                     timeZone
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
#         else:
#             preferred_dt_start = base_date
#             preferred_dt_end = end_of_base_date

#         # Pass datetime range instead of just a date
#         results = get_available_slots(
#             doctor_id=doctor_id,
#             date_time_start=preferred_dt_start,
#             date_time_end=preferred_dt_end,
#             is_couple=is_couple,
#             timezone_str=timeZone,
#             buffer=timedelta(hours=0)
#         )

#         # If slots are empty, try next available date from generate slots function
#         results['current_date'] = str(preferred_dt_start.date())
#         slots = results.get('slots', [])
#         available_dates = results.get('available_dates', [])

#         next_date_found = False
#         if not slots and available_dates:
#             for next_date in available_dates:
#                 try:
#                     next_dt_start = convert_local_dt_to_utc(
#                         f"{next_date}T00:00:00",
#                         timeZone
#                     )
#                     next_dt_end = convert_local_dt_to_utc(
#                         f"{next_date}T23:59:59",
#                         timeZone
#                     )
#                 except ValueError:
#                     continue
#                 print("timezone", timeZone)
#                 next_results = get_available_slots(
#                     doctor_id=doctor_id,
#                     date_time_start=next_dt_start,
#                     date_time_end=next_dt_end,
#                     is_couple=is_couple,
#                     timezone_str=timeZone
#                 )
#                 next_slots = next_results.get('slots', [])
#                 if next_slots:
#                     results = next_results
#                     results['current_date'] = str(next_dt_start.date())
#                     next_date_found = True
#                     break

#         if not next_date_found:
#             results['current_date'] = str(preferred_dt_start.date())

#         return Response({
#             "available_slots": results,
#         }, status=status.HTTP_200_OK)





# from analysis.models import Reschedule_history
# from general.gmeet.gmeet import generate_google_meet
# from django.utils import  timezone
# from general.tasks import send_appointment_rescheduled_email_task


# class AppointmentRescheduleView_Customer(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         """
#         API to reschedule an appointment.
#         Expects:
#             - appointment_id: ID of the appointment to reschedule
#         """
#         from django.utils import  timezone        
#         appointment_id = request.data.get('appointment_id')
#         reason   = request.data.get('reason')
#         initiate = request.data.get('initiate')
    

#         if initiate :
        
#             try:
#                 appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)

#                 print(appointment.start_time )
#                 print(timezone.now())

#             except AppointmentHeader.DoesNotExist:
#                 return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

#             if appointment.appointment_status in ['completed', 'cancelled' , 'rescheduled_by_doctor' ,"rescheduled_by_customer"]:
#                 return Response({"error": "Cannot reschedule a completed or cancelled or rescheduled appointment."}, status=status.HTTP_400_BAD_REQUEST)
            
#             if appointment.start_time < timezone.now() - timedelta(hours=6):
#                 return Response({"error": "Reschedule only allowed 6 hours before appointment."}, status=status.HTTP_400_BAD_REQUEST)
#             if appointment.start_time < timezone.now():
#                 return Response({"error": "Appointment date is past.Reschedule not allowed."}, status=status.HTTP_400_BAD_REQUEST)

#             if Reschedule_history.objects.filter(appointment=appointment).exists():
#                 return Response({"error": "You have reached the maximum number of reschedules allowed."}, status=status.HTTP_400_BAD_REQUEST)

#             # Update appointment details
#             appointment.appointment_status = 'rescheduled_by_customer'
#             appointment.meeting_link = ''
        
#             appointment.save()

#             Reschedule_history.objects.create(appointment = appointment , reason = reason , initiated_by = 'customer' )
        
#             return Response({
#                 "message": "Appointment reschedule initiated.",
#                 "appointment_id": appointment.appointment_id
#             }, status=status.HTTP_200_OK)
        
#         else:
        
           

#             appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)

#             if appointment.appointment_status not in ['rescheduled_by_customer','rescheduled_by_doctor']:
#                 print(appointment.appointment_status)
#                 return Response({"error": "Reschedule not initiated."}, status=status.HTTP_400_BAD_REQUEST)
#             if appointment.appointment_status == 'completed' or appointment.appointment_status == 'cancelled' :
#                 return Response({"error": "Appointment already completed or cancelled."}, status=status.HTTP_400_BAD_REQUEST)

#             slot = request.data.get('slot')
#             date_str = slot.get('date')
#             start_str = slot.get('start') 
#             end_str = slot.get('end')

#             print(date_str, start_str, end_str)
#             time_zone = get_customer_timezone(request.user)
#             start_datetime_utc = convert_local_dt_to_utc(date_time_str=start_str , tz_str=time_zone)
#             end_datetime_utc = convert_local_dt_to_utc(date_time_str=end_str , tz_str=time_zone)
            
#             # Extract date and time components for database operations
#             start_time = start_datetime_utc
#             end_time = end_datetime_utc

#             overlapping = DoctorAppointment.objects.filter(
#                 doctor=appointment.doctor,
#                 start_time__lt=end_time,
#                 end_time__gt=start_time
#             ).exists()
#             if overlapping:
#                 return Response({"error": "Doctor is not available at this time. Slot already booked"}, status=status.HTTP_400_BAD_REQUEST)
#             DoctorAppointment.objects.filter(appointment=appointment , confirmed = True).delete()

#             new_d_a = DoctorAppointment.objects.create(
#                 doctor=appointment.doctor,
#                 specialization=appointment.specialization,
#                 start_time=start_time,
#                 end_time=end_time,
#                 appointment=appointment,
#                 confirmed = True
#             )


#             aware_from = start_datetime_utc
#             aware_to = end_datetime_utc

#             appointment.appointment_status = 'confirmed'
#             meeting_creds = generate_google_meet(
#                 summary='Appointment',
#                 description='Appointment with doctor',
#                 start_time=aware_from,
#                 end_time=aware_to
#             )
#             appointment.meeting_link = meeting_creds.get('meeting_link', '')
#             meeting_tracker = track_map_meeting(appointment_id , appointment.meeting_link , meeting_creds.get('meeting_code', ''))

#             send_appointment_rescheduled_email_task.delay(
#                 appointment_id = appointment.appointment_id,
#                 previous_date = appointment.start_time.date().strftime('%Y-%m-%d'),
#                 previous_time = appointment.start_time.time().strftime('%H:%M:%S'),
#                 new_date = start_time.date().strftime('%Y-%m-%d'),
#                 new_time = start_time.time().strftime('%H:%M:%S')
#             )
#             appointment.end_time = end_time
#             appointment.start_time = start_time 
#             appointment.save()
#         return Response('Successfully rescheduled appointment' , status=status.HTTP_200_OK)






# class Get_contact_details(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
#             customer_profile = CustomerProfile.objects.get(user=request.user)
#             data = {
#                 "email": customer_profile.email,
#                 "phone_number": customer_profile.mobile_number,
#                 "country_code": customer_profile.country_details.country_code if customer_profile.country_details else None,
#                 "whatsapp_number": customer_profile.whatsapp_number,
#             }
#             return Response(data, status=status.HTTP_200_OK)
#         except CustomerProfile.DoesNotExist:
#             return Response({"error": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)



# from analysis.models import Cancel_history
# from .models import Refund
# from general.finance.controllers import refund_controller
# from general.emal_service import send_appointment_cancellation_email
# from general.tasks import send_appointment_cancellation_email_task
# from celery import current_app

# class Cancel_Appointment(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         appointment_id = request.data.get('appointment_id')

#         try:
#             appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#             doctor_appointment = DoctorAppointment.objects.get(appointment=appointment)
#             reschedule_history = Reschedule_history.objects.filter(appointment=appointment).exists()
#             meeting_tracker = Meeting_Tracker.objects.get(appointment=appointment)
            
#             if reschedule_history:
#                 return Response({"error": "You cannot cancel an already rescheduled appointment."}, status=status.HTTP_400_BAD_REQUEST)
#             if appointment.appointment_status == 'cancelled_by_customer':
#                 return Response({"error": "Appointment already cancelled by customer."}, status=status.HTTP_400_BAD_REQUEST)
#             if appointment.appointment_status == 'completed':
#                 return Response({"error": "Appointment already completed."}, status=status.HTTP_400_BAD_REQUEST)

#             if not appointment.start_time - timedelta(hours=24) > timezone.now():
#                 return Response({"error": "Cancellation is only allowed before 24 hours."}, status=status.HTTP_400_BAD_REQUEST)
#             if appointment.start_time.date() == timezone.now().date():
#                 return Response({"error": "Appointment date is today.Cancelation not allowed."}, status=status.HTTP_400_BAD_REQUEST)
#             if appointment.start_time.date() < timezone.now().date():
#                 return Response({"error": "Appointment date is past.Cancelation not allowed."}, status=status.HTTP_400_BAD_REQUEST)

            



#             doctor_appointment.delete()
#             appointment.appointment_status = 'cancelled_by_customer'
#             if appointment.referral and appointment.referral.converted_to_appointment:
#                 appointment.referral.converted_to_appointment = False
#                 appointment.referral.save()
#             appointment.save()
            
#             reason = request.data.get('reason')
#             Cancel_history.objects.create(appointment = appointment , reason = reason )
#             transaction = PreTransactionData.objects.filter(appointment=appointment).first()
#             if  timezone.now() < appointment.start_time-timedelta(hours=72):
#                 refund_amount = float(transaction.total_amount)
#             else:
#                 refund_amount = float(transaction.total_amount) / 2
#             refund = Refund.objects.create(appointment = appointment , refund_amount = refund_amount , refund_currency = transaction.currency , refund_status = 'pending' , request_date = timezone.now() )
#             # print(refund_controller(pretransaction_id=transaction.pretransaction_id))
#             send_appointment_cancellation_email_task.delay(
#                 appointment_id = appointment.appointment_id,
#             )
#             current_app.control.revoke(meeting_tracker.monitor_task_id, terminate=True)
#             current_app.control.revoke(meeting_tracker.reminder_task_id, terminate=True)



#             return Response({"message": "Appointment cancelled successfully."}, status=status.HTTP_200_OK)
#         except AppointmentHeader.DoesNotExist:
#             return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)




# from rest_framework.decorators import api_view
# from general.smss import appointmentbooked
# from general.utils import is_doctor_available
# @api_view(['POST'])
# def Add_slot(request):
#     appointment_id = request.data.get('appointment_id')
#     slot = request.data.get('slot')
#     date_str = slot.get('date')
#     start_str = slot.get('start') 
#     end_str = slot.get('end')
    
#     try:
#         customer = CustomerProfile.objects.get(user=request.user)
#     except CustomerProfile.DoesNotExist:
#         return Response({"error": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)

#     start_datetime_utc = convert_local_dt_to_utc_return_dt( start_str, customer.time_zone)
#     end_datetime_utc = convert_local_dt_to_utc_return_dt( end_str, customer.time_zone)
    
#     # Extract date and time components for database operations
#     date = start_datetime_utc.date()
#     start_time = start_datetime_utc
#     end_time = end_datetime_utc

#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id=appointment_id)
#         if DoctorAppointment.objects.filter(appointment=appointment ).exists():
#             return Response({"error": "Slot already booked."}, status=status.HTTP_400_BAD_REQUEST)
#         print(start_time)
#         print(end_time)
#         doctor_available = is_doctor_available(doctor_id=appointment.doctor , date_obj=date , from_time=start_time , to_time=end_time)
#         if doctor_available:
#             DoctorAppointment.objects.create(
#                 doctor=appointment.doctor,
#                 specialization=appointment.specialization,
#                 date=date,
#                 start_time=start_time,
#                 end_time=end_time,
#                 appointment=appointment,
#                 confirmed = True
#             )
#         else:
#             return Response({"error": "Doctor is not available at this time. Slot already booked, please select another slot."}, status=status.HTTP_400_BAD_REQUEST)

       
    
  
#     except AppointmentHeader.DoesNotExist:
#         return Response({"error": "Appointment not found for the given appointment ID."}, status=404)
  
#     if appointment.payment_done:
#         appointment.appointment_status = 'confirmed'
        
#         # Create timezone-aware datetime objects using the UTC date and time
#         # We can use the already converted UTC datetime objects from earlier
#         aware_from = timezone.make_aware(datetime.combine(date, start_time)) if not start_datetime_utc.tzinfo else start_datetime_utc
#         aware_to = timezone.make_aware(datetime.combine(date, end_time)) if not end_datetime_utc.tzinfo else end_datetime_utc
        
#         appointment.meeting_link = generate_google_meet(
#             summary='Appointment',
#             description='Appointment with doctor',
#             start_time=aware_from,
#             end_time=aware_to
#         )
#         meeting_tracker = track_map_meeting(appointment_id , appointment.meeting_link , appointment.meeting_id)

#         appointment.save()
#     else:
#         appointment.appointment_status = "pending_payment"

#     appointment.appointment_date = date
#     appointment.appointment_time = start_time
#     appointment.end_time = end_time
#     appointment.start_time = start_time  # <-- was wrongly set to `end_time` in your code
#     appointment.save()
   
#     if appointment.confirmation_method == "SMS":
#         appointmentbooked(appointment.appointment_id)
#     elif appointment.confirmation_method == "Email":
#         send_appointment_confirmation_email(
#             name=f"{appointment.user.first_name} {appointment.user.last_name}",
#             to_email=appointment.email,
#             doctor_flag=appointment.doctor.doctor_flag,
#             doctor_name=f"{appointment.doctor.user.first_name} {appointment.doctor.user.last_name}",
#             date=appointment.appointment_date,
#             time=appointment.from_time,
#             meet_link=meeting_tracker.customer_meeting_link,

#         )
    
#     return Response('Successfully booked appointment' , status=status.HTTP_200_OK)





# from rest_framework.decorators import permission_classes

# @api_view(['POST'])
# def create_partner_two(request):
    
#     first_name      = request.data.get('first_name')
#     last_name       = request.data.get('last_name')
#     email           = request.data.get('email')
#     phone_number    = request.data.get('phone_number')
#     gender          = request.data.get('gender')
#     dob             = request.data.get('dob')
#     address         = request.data.get('address')
#     country         = request.data.get('country')
#     preferred_name  = request.data.get('preferred_name')
#     partners_id     = request.data.get('partners_id')
#     whatsapp_number = request.data.get('whatsapp_number')
    
    
#     required_fields = [
#         'first_name', 'last_name',  
#         'country','gender', 'dob']
#     for field in required_fields:
#         if not request.data.get(field):
#             return Response({"error": f"{field} is required."}, status=status.HTTP_400_BAD_REQUEST)
#     try:
#         partner = CustomerProfile.objects.get(id = partners_id)
#         user = User.objects.create(
#             first_name=first_name,
#             last_name=last_name,
#             username=email if email else whatsapp_number,
#             email=email
#         )
#         customer = CustomerProfile.objects.create(
#             user=user,
#             mobile_number=phone_number,
#             email=email,
#             date_of_birth=dob,
#             address=address,
#             country_details=Countries.objects.get(country_name=country),
#             gender = gender,
#             preferred_name=preferred_name,
#             partner=partner,
#             whatsapp_number=whatsapp_number,
#             confirmation_method =(
#                 "both" if email and whatsapp_number
#                 else "email" if email
#                 else "whatsapp" if whatsapp_number
#                 else "none"
#             ))

#         partner.partner = customer
#         partner.save()

#         return Response({
#             "message": "Partner Two created successfully.",
#             "customer_id": customer.id,
#             "email": email,
#             "phone_number": phone_number
#         }, status=status.HTTP_201_CREATED)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def does_partner_exist(request):
#     """
#     API to check if a partner exists for the logged-in user.
#     Returns:
#         - True if partner exists, False otherwise.
#     """
#     try:
#         customer_profile = CustomerProfile.objects.get(user=request.user)
#         if customer_profile.partner:
#             return Response({"partner_exists": True}, status=status.HTTP_200_OK)
#         else:
#             return Response({"partner_exists": False}, status=status.HTTP_200_OK)
#     except CustomerProfile.DoesNotExist:
#         return Response({"error": "Customer profile not found."}, status=status.HTTP_404_NOT_FOUND)







# from analysis.models import Prescribed_Medications,Prescribed_Tests,Notes_for_patient,Follow_Up_Notes
# from .serializers import PrescribedMedicationsSerializer,PrescribedTestsSerializer,NotesForPatientSerializer,Followup_notes_serializer,PatientSerializer
# from collections import defaultdict
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# class Get_Prescriptions(APIView):
#     # permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
#             customer = CustomerProfile.objects.get(id=request.GET.get('cid'))
#         except CustomerProfile.DoesNotExist:
#             return Response(
#                 {'error': 'Invalid customer ID'}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Query with doctor
#         tests = Prescribed_Tests.objects.filter(customer=customer,submitted = False).select_related("doctor")
#         medicines = Prescribed_Medications.objects.filter(customer=customer,is_active = True).select_related("doctor")
#         patient_notes = Notes_for_patient.objects.filter(customer=customer).select_related("doctor")
#         # Group by doctor with serialized data
#         tests_by_doctor = []
#         for test in tests:
#             tests_by_doctor.append(PrescribedTestsSerializer(test).data)

#         medicine_by_doctor =[]
#         for med in medicines:
#             medicine_by_doctor.append(PrescribedMedicationsSerializer(med).data)

#         notes_by_doctor = []
#         for note in patient_notes:
#             notes_by_doctor.append(NotesForPatientSerializer(note).data)

#         # Convert defaultdict to dict so it's JSON serializable
#         # tests_by_doctor = dict(tests_by_doctor)
#         # medicine_by_doctor = dict(medicine_by_doctor)
#         # notes_by_doctor = dict(notes_by_doctor)


#         prescriptions_per_doctor = defaultdict(lambda: {"doctor": None, "medicines": [], "tests": [], "notes": []})
#         for medicine in medicine_by_doctor:
#             # single_doctor = {}
#             prescriptions_per_doctor[medicine['doctor_id']]['medicines'].append(medicine)
#             prescriptions_per_doctor[medicine['doctor_id']]['doctor'] = medicine['doctor']

#         for test in tests_by_doctor:
#             prescriptions_per_doctor[test['doctor_id']]['tests'].append(test)
#             prescriptions_per_doctor[test['doctor_id']]['doctor'] = test['doctor']
#         for note in notes_by_doctor:
#             prescriptions_per_doctor[note['doctor_id']]['notes'].append(note)
#             prescriptions_per_doctor[note['doctor_id']]['doctor'] = note['doctor']

#         prescriptions_per_doctor = dict(prescriptions_per_doctor)      
#         prescriptions_per_doctor_list = []
#         for key, value in prescriptions_per_doctor.items():
#             prescriptions_per_doctor_list.append(value)
        
#         customer_data = PatientSerializer(customer).data

#         return Response({
#             # "tests": tests_by_doctor,
#             # "medicine": medicine_by_doctor,
#             # "patient_notes": notes_by_doctor,
#             "prescriptions": prescriptions_per_doctor_list,
#             "patient_first_name": customer.user.first_name,
#             "patient_last_name": customer.user.last_name,
#             "patient_details": customer_data
#         })

# from django.shortcuts import render
# from django.http import HttpResponse
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.template.loader import render_to_string
# import pdfkit


# class Get_Prescriptions_pdf(APIView):
#     # permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
#             customer = CustomerProfile.objects.get(id=request.GET.get('cid'))
#             doctor = DoctorProfiles.objects.get(doctor_profile_id=request.GET.get('did'))
#             latest_appointment = AppointmentHeader.objects.filter(customer=customer, doctor=doctor , completed = True).latest('start_time')
#         except CustomerProfile.DoesNotExist:
#             return HttpResponse('<h1>Error: Invalid customer ID</h1>', status=status.HTTP_400_BAD_REQUEST)
#         except DoctorProfiles.DoesNotExist:
#             return HttpResponse('<h1>Error: Invalid doctor ID</h1>', status=status.HTTP_400_BAD_REQUEST)

#         tests = Prescribed_Tests.objects.filter(customer=customer, doctor=doctor, submitted=False).select_related("doctor")
#         medicines = Prescribed_Medications.objects.filter(customer=customer, doctor=doctor, is_active=True).select_related("doctor")
#         patient_notes = Notes_for_patient.objects.filter(customer=customer, doctor=doctor).select_related("doctor")
#         follow_notes = Follow_Up_Notes.objects.filter(customer=customer, appointment__doctor=doctor)

#         tests_data = PrescribedTestsSerializer(tests, many=True).data
#         medicines_data = PrescribedMedicationsSerializer(medicines, many=True).data
#         notes_data = NotesForPatientSerializer(patient_notes, many=True).data
#         follow_notes_data = Followup_notes_serializer(follow_notes, many=True).data
#         customer_data = PatientSerializer(customer).data

#         doctor_specializations = [spec.specialization.specialization for spec in doctor.doctor_specializations.all()]
        
#         print(latest_appointment.followup)
#         context = {
#             "medicines": medicines_data,
#             "tests": tests_data,
#             "notes": notes_data,
#             "follow_notes": follow_notes_data,
#             "patient_first_name": customer.user.first_name,
#             "patient_last_name": customer.user.last_name,
#             "patient_details": customer_data,
#             "doctor_name": f"{doctor.first_name} {doctor.last_name}".strip(),
#             "doctor_specializations": doctor_specializations,
#             'doctor_qualification': doctor.qualification,
#             "reg_no": doctor.registration_number,
#             "salutation": doctor.salutation,
#             "doctor_phone": doctor.mobile_number if doctor.mobile_number else ' ',
#             "doctor_email": doctor.email_id,
#             'doctor_signature': doctor.sign_file_name.url if doctor.sign_file_name else None,
#             "backend_url": settings.BACKEND_URL,
#             "cunsultation_type":'Video',
#             "status":latest_appointment.followup,
#             'date':latest_appointment.start_time.date()
           

#         }
#         path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
      
#         print(context['doctor_signature'])
        
       

#         # print(context['doctor_signature'],'\n\n',settings.BASE_DIR ,'\n\n',logo_path , '\n\n' ,logo_uri , '\n\n')
#         config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

#         # Render HTML as string
#         html_string = render_to_string('prescription.html', context)

#         # Generate PDF
#         # pdf = pdfkit.from_string(html_string, False)
#         pdf = pdfkit.from_string(html_string, False, configuration=config)
#         response = HttpResponse(pdf, content_type='application/pdf')
#         response['Content-Disposition'] = 'inline; filename="prescription.pdf"'
#         return response
#         # return render(request, 'prescription.html', context)

# from .serializers import SpecializationsSerializerFull
# from administrator.models import Specializations
# @api_view(['GET'])
# def get_specializations(request):
#     specializations = Specializations.objects.exclude(specialization = 'No Specialization')
#     serializer = SpecializationsSerializerFull(specializations, many=True)
#     return Response(serializer.data)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def relieve_package(request):
#     appointment_id = request.GET.get('appointment')
#     try:
#         appointment = AppointmentHeader.objects.get(appointment_id = appointment_id)
#     except AppointmentHeader.DoesNotExist:
#         return Response({'message': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
#     if appointment.appointment_status == 'confirmed':
#         return Response({'message': 'Appointment already confirmed'}, status=status.HTTP_400_BAD_REQUEST)
    
#     if appointment.package_included:
#         appointment.package_included = False
#         appointment.package = None
#         appointment.save()
#     return Response({'message': 'Package relieved successfully'}, status=status.HTTP_200_OK)

# @api_view(['GET'])
# def get_specialization_from_id(request):
#     specialization_id = request.GET.get('specialization_id')
#     try:
#         specialization = Specializations.objects.get(specialization_id=specialization_id)
#     except Specializations.DoesNotExist:
#         return Response({'message': 'Specialization not found'}, status=status.HTTP_404_NOT_FOUND)
#     return Response({'specialization': SpecializationsSerializerFull(specialization).data}, status=status.HTTP_200_OK)


# from doctor.models import DoctorPaymentRules
# from .models import Suggested_packages
# from doctor.serializers import DoctorPaymentRulesSerializer

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_all_packages(request):
#     doctor_id = request.GET.get('doctor_id')
#     specialization_id = request.GET.get('specialization_id')
#     try:
#         customer = CustomerProfile.objects.get(user = request.user)
#         doctor = DoctorProfiles.objects.get(doctor_profile_id = doctor_id)
#         specialization = Specializations.objects.get(specialization_id = specialization_id)
#     except CustomerProfile.DoesNotExist:
#         return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
#     except DoctorProfiles.DoesNotExist:
#         return Response({'message': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
#     except Specializations.DoesNotExist:
#         return Response({'message': 'Specialization not found'}, status=status.HTTP_404_NOT_FOUND)

#     all_packages = DoctorPaymentRules.objects.filter(doctor = doctor, specialization = specialization , country= customer.country_details)
#     serialized_packages = DoctorPaymentRulesSerializer(all_packages, many=True).data
    
#     # Add suggested flag to each package based on Suggested_packages table
#     for package in serialized_packages:
#         suggested = Suggested_packages.objects.filter(
#             # session_count__gt=1,
#             suggested_by=doctor,
#             customer=customer, 
#             package_id=package['id']
#         ).exists()
#         package['suggested'] = suggested  

#     return Response({
#         'packages': serialized_packages
#     }, status=status.HTTP_200_OK)



# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def edit_email_whatsapp(request):
#     user = request.user
#     customer = CustomerProfile.objects.get(user = user)
#     email = request.data.get('email')
#     whatsapp = request.data.get('whatsapp')
#     confirmation_method = request.data.get('confirmation_method')
#     if confirmation_method:
#         customer.confirmation_method = confirmation_method
#         message = 'Confirmation method updated successfully'
#     if email:
#         customer.email = email
#         message = 'Email updated successfully'
#     if whatsapp:
#         customer.mobile_number = whatsapp
#         message = 'WhatsApp updated successfully'
#     if email or whatsapp or confirmation_method:
#         customer.save()
#         return Response({'message': message}, status=status.HTTP_200_OK)
#     return Response({'message': 'No email, WhatsApp or confirmation method provided'}, status=status.HTTP_400_BAD_REQUEST)
