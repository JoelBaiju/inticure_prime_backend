# ef payment2(request,temp_id):
#     appointment_flag = request.GET.get('appointment_flag')
#     new_data = request.GET.get('new_data')
#     print('appointment_flag',appointment_flag)
#     print('new_data',new_data)

#     transaction_qset=TemporaryTransactionData.objects.get(temp_id=temp_id)
#     client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
#     payment_order = client.order.create({
#         'amount': transaction_qset.total_amount*100,
#         'currency': "INR",
#         'receipt': "order_receipt",
#         'payment_capture': '1' 
#     })
#     data = {}
#     data['key'] = settings.RAZORPAY_API_KEY
#     data['razorpay_customer_token_id'] = payment_order['id']
#     data['amount'] = transaction_qset.total_amount*100
#     data['temp_id'] = temp_id
#     data['currency'] = transaction_qset.currency
#     data['user_id'] = 0
#     data['appointment_flag'] = appointment_flag
#     print('data',data)
#     return render(request, 'razorpayment/payment2.html', data)








# def checkout_preprocess2(user_id,amount,temp_id,currency,appointment_flag):
#     customer_email = User.objects.get(id=user_id).email
#     razorpay.api_key = settings.RAZORPAY_API_KEY
#     razorpay_customer = RazorpayCustomer.objects.filter(customer_id=user_id)
#     if razorpay_customer.count() > 0:
#         razorpay_customer_token_id = razorpay_customer.first().razorpay_customer_token_id
#     else:
#         receipt = "receipt_001"
#         razorpay_order = razorpay_client.order.create(
#             dict(amount=amount*100, currency=currency, receipt=receipt, payment_capture="1")
#         )
#         print(razorpay_order)
#         razorpay_customer_token_id = razorpay_order['id']
#         RazorpayCustomer.objects.create(customer_id=user_id,
#                                       razorpay_customer_token_id=razorpay_customer_token_id)
#     data = {}
#     data['key'] = settings.RAZORPAY_API_KEY
#     data['razorpay_customer_token_id'] = razorpay_customer_token_id
#     data['amount'] = amount*100
#     data['temp_id'] = temp_id
#     data['currency'] = currency
#     data['user_id'] = user_id
#     data['appointment_flag'] = appointment_flag
#     return data

# def payment_page(request,temp_id):
#     appointment_flag = request.GET.get('appointment_flag')
#     new_data = request.GET.get('new_data')
#     print('appointment_flag',appointment_flag)
#     print('new_data',new_data)
#     transaction_qset=TemporaryTransactionData.objects.get(temp_id=temp_id)
#     print(transaction_qset.user_id,transaction_qset.total_amount,transaction_qset.currency,appointment_flag)
#     data = checkout_preprocess2(transaction_qset.user_id,
#     transaction_qset.total_amount,temp_id,transaction_qset.currency,appointment_flag)
#     print('data',data)
#     return render(request, 'razorpayment/payment.html', data)

# @csrf_exempt
# def verify_payment(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         print("Received Data:", data)
#         try:
#             razorpay_client.utility.verify_payment_signature({
#                 'razorpay_order_id': data['razorpay_order_id'],
#                 'razorpay_payment_id': data['razorpay_payment_id'],
#                 'razorpay_signature': data['razorpay_signature']
#             })
#             return JsonResponse({"status": "success"})
#         except SignatureVerificationError:
#             return JsonResponse({"status": "failed", "message": "Signature verification failed"})
#     return JsonResponse({"error": "Invalid request method."}, status=400)
