from administrator.models import Countries, GeneralPaymentRules, Specializations

def populate_general_payment_rules_for_euro_countries():
    # Fetch all countries using Euro
    euro_countries = Countries.objects.filter(currency__iexact="EUR")

    # Define your 5 base payment rules (for cloning)
    base_rules = [
        {
            "specialization_id": 4,
            "doctor_flag": "senior",
            "experience": "high",
            "doctor_fee_couple": 800,
            "doctor_fee_single": 1300,
            "user_total_fee_single": 50,
            "user_total_fee_couple": 75,
            "pricing_name": "",
            "session_count": 1,
            "actual_price_couple": None,
            "actual_price_single": None,
        },
        {
            "specialization_id": 4,
            "doctor_flag": "senior",
            "experience": "high",
            "doctor_fee_couple": 3570,
            "doctor_fee_single": 2380,
            "user_total_fee_single": 130,
            "user_total_fee_couple": 195,
            "pricing_name": "",
            "session_count": 3,
            "actual_price_couple": 225,
            "actual_price_single": 150,
        },
        {
            "specialization_id": 4,
            "doctor_flag": "senior",
            "experience": "high",
            "doctor_fee_couple": 7145,
            "doctor_fee_single": 4765,
            "user_total_fee_single": 265,
            "user_total_fee_couple": 395,
            "pricing_name": "",
            "session_count": 6,
            "actual_price_couple": 450,
            "actual_price_single": 300,
        },
        {
            "specialization_id": 4,
            "doctor_flag": "senior",
            "experience": "high",
            "doctor_fee_couple": 10720,
            "doctor_fee_single": 7145,
            "user_total_fee_single": 395,
            "user_total_fee_couple": 595,
            "pricing_name": "",
            "session_count": 9,
            "actual_price_couple": 675,
            "actual_price_single": 450,
        },
        {
            "specialization_id": 4,
            "doctor_flag": "senior",
            "experience": "high",
            "doctor_fee_couple": 14295,
            "doctor_fee_single": 9495,
            "user_total_fee_single": 495,
            "user_total_fee_couple": 795,
            "pricing_name": "",
            "session_count": 12,
            "actual_price_couple": 900,
            "actual_price_single": 600,
        },
    ]

    created_count = 0
    skipped_count = 0

    for country in euro_countries:
        for rule in base_rules:
            # Avoid duplicates (because of unique_together constraint)
            exists = GeneralPaymentRules.objects.filter(
                country=country,
                specialization_id=rule["specialization_id"],
                experience=rule["experience"],
                doctor_flag=rule["doctor_flag"],
                session_count=rule["session_count"]
            ).exists()

            if exists:
                skipped_count += 1
                continue

            GeneralPaymentRules.objects.create(
                country=country,
                specialization_id=rule["specialization_id"],
                experience=rule["experience"],
                doctor_flag=rule["doctor_flag"],
                session_count=rule["session_count"],
                doctor_fee_single=rule["doctor_fee_single"],
                doctor_fee_couple=rule["doctor_fee_couple"],
                user_total_fee_single=rule["user_total_fee_single"],
                user_total_fee_couple=rule["user_total_fee_couple"],
                pricing_name=rule["pricing_name"],
                actual_price_single=rule["actual_price_single"],
                actual_price_couple=rule["actual_price_couple"],
            )
            created_count += 1

    print(f"✅ Done! Created {created_count} new rules, skipped {skipped_count} duplicates.")

