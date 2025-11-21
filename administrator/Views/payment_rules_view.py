from doctor.models import DoctorProfiles , DoctorPaymentRules
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from administrator.models import GeneralPaymentRules
from ..serializers import doctor_country_payment_rule_serializer


# @permission_classes([IsAuthenticated, IsAdminUser])
@api_view(['GET'])
def doctor_payment_rules(request):
    """
    GET /api/administrator/payment/doctor-rules/?doctor_id=1
    Returns doctor rules grouped exactly like GeneralPaymentRules API
    """
    doctor_id = request.GET.get('doctor_id')
    if not doctor_id:
        return Response({"error": "doctor_id parameter is required"}, status=400)

    try:
        doctor = DoctorProfiles.objects.get(doctor_profile_id=doctor_id)
    except DoctorProfiles.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=404)

    # Fetch rules
    rules = DoctorPaymentRules.objects.select_related("specialization", "country").filter(doctor=doctor)

    # GROUPING DICT
    grouped = {}

    for rule in rules:
        spec_id = rule.specialization.specialization_id if rule.specialization else None
        if not spec_id:
            continue

        # Create specialization block
        if spec_id not in grouped:
            grouped[spec_id] = {
                "specialization_id": spec_id,
                "specialization_name": rule.specialization.specialization,
                "payment_rules": {}
            }

        country_id = rule.country.id if rule.country else None
        if not country_id:
            continue

        # Create country block under specialization
        if country_id not in grouped[spec_id]["payment_rules"]:
            grouped[spec_id]["payment_rules"][country_id] = {
                "country_id": country_id,
                "country_name": rule.country.country_name,
                "currency_symbol": rule.country.currency_symbol,
                "specialization": rule.specialization.specialization,
                "specialization_id": spec_id,
                "rules": []
            }

        # Append current rule
        grouped[spec_id]["payment_rules"][country_id]["rules"].append(rule)

    # Convert dict to list + serialize
    final_data = []

    for spec_id, spec_block in grouped.items():
        country_blocks = list(spec_block["payment_rules"].values())
        spec_block["payment_rules"] = doctor_country_payment_rule_serializer(country_blocks, many=True).data
        final_data.append(spec_block)

    return Response(final_data)
