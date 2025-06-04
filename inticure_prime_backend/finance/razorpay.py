# import razorpay
# from django.conf import settings

# # Initialize client
# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

# def initiate_razorpay_payment(request, temp_id):
#     # Get transaction details
#     transaction = TemporaryTransactionData.objects.get(temp_id=temp_id)
    
#     # Create Razorpay order
#     payment_order = razorpay_client.order.create({
#         'amount': transaction.total_amount * 100,  # Convert to paise
#         'currency': "INR",
#         'receipt': "order_receipt",
#         'payment_capture': '1'
#     })
    
#     # Prepare payment data
#     payment_data = {
#         'key': settings.RAZORPAY_API_KEY,
#         'amount': transaction.total_amount * 100,
#         'currency': transaction.currency,
#         'order_id': payment_order['id'],
#         'temp_id': temp_id
#     }
    
#     return payment_data  # Pass this to frontend