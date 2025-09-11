import re
from customer.models import Refund
from doctor.models import Payouts
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from administrator.serializers import RefundSerializer, PayoutsSerializer
from django.utils import timezone


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_refunds_view(request):
    status_filter = request.GET.get('status')
    if status_filter:
        refunds = Refund.objects.filter(refund_status=status_filter)
    else:
        refunds = Refund.objects.filter(refund_status='pending')

    serializer = RefundSerializer(refunds, many=True)
    return Response(serializer.data)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payout_view(request):
    status_filter = request.GET.get('status')
    if status_filter:
        payouts = Payouts.objects.filter(status=status_filter)
    else:
        payouts = Payouts.objects.filter(status='pending')
    serializer = PayoutsSerializer(payouts, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_payout(request):
    payout_id = request.data.get('payout_id')
    try:
        payout = Payouts.objects.get(id=payout_id)
        payout.status = 'completed'
        payout.completed_at = timezone.now()
        payout.save()
    except Payouts.DoesNotExist:
        return Response('payout not found')
    return Response('payout completed')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_refund_status(request):
    refund_id = request.data.get('refund_id')
    refund_status = request.data.get('refund_status')
    try:
        refund = Refund.objects.get(id=refund_id)
        refund.refund_status = refund_status
        refund.refund_date = timezone.now()
        refund.save()
    except Refund.DoesNotExist:
        return Response('refund not found')
    return Response('refund status updated')
