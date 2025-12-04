from django.core.management.base import BaseCommand
from doctor.models import GeneralPaymentRules, DoctorPaymentRules, Countries


class Command(BaseCommand):
    help = "Syncs doctor fees (single/couple) for all countries & all doctors based on India's pricing rules."

    def handle(self, *args, **kwargs):

        # -----------------------------
        # 1. Find India
        # -----------------------------
        try:
            india = Countries.objects.get(country_name__iexact="india")
        except Countries.DoesNotExist:
            self.stdout.write(self.style.ERROR("India country record not found!"))
            return

        india_rules = GeneralPaymentRules.objects.filter(country=india)

        if not india_rules.exists():
            self.stdout.write(self.style.ERROR("No GeneralPaymentRules exist for India."))
            return

        # -----------------------------
        # PHASE 1: Update GeneralPaymentRules
        # -----------------------------
        updated_general = 0

        for india_rule in india_rules:
            matching_rules = GeneralPaymentRules.objects.filter(
                specialization=india_rule.specialization,
                experience=india_rule.experience,
                doctor_flag=india_rule.doctor_flag,
                session_count=india_rule.session_count
            ).exclude(country=india)

            for rule in matching_rules:
                rule.doctor_fee_single = india_rule.doctor_fee_single
                rule.doctor_fee_couple = india_rule.doctor_fee_couple
                rule.save()
                updated_general += 1

        self.stdout.write(self.style.SUCCESS(
            f"Updated {updated_general} GeneralPaymentRules to match India."
        ))

        # -----------------------------
        # PHASE 2: Update DoctorPaymentRules
        # -----------------------------
        updated_doctor_rules = 0

        for india_rule in india_rules:

            # Find doctors using the same attributes
            doctor_matches = DoctorPaymentRules.objects.filter(
                specialization=india_rule.specialization,
                session_count=india_rule.session_count
            ).exclude(country=india)

            for d_rule in doctor_matches:
                # =========== ONLY update doctor's fees ================
                d_rule.custom_doctor_fee_single = india_rule.doctor_fee_single
                d_rule.custom_doctor_fee_couple = india_rule.doctor_fee_couple


                d_rule.save()
                updated_doctor_rules += 1

        self.stdout.write(self.style.SUCCESS(
            f"Updated {updated_doctor_rules} DoctorPaymentRules to match India doctor fees."
        ))

        # -----------------------------
        # DONE
        # -----------------------------
        self.stdout.write(self.style.SUCCESS("Doctor fee sync completed successfully."))
