from django.core.management.base import BaseCommand
from ...models import GeneralPaymentRules, Countries


class Command(BaseCommand):
    help = "Syncs doctor fee and user fees for all countries based on India's pricing rules."

    def handle(self, *args, **kwargs):

        try:
            india = Countries.objects.get(country_name__iexact="India")
        except Countries.DoesNotExist:
            self.stdout.write(self.style.ERROR("India country record not found!"))
            return

        india_rules = GeneralPaymentRules.objects.filter(country=india)

        if not india_rules.exists():
            self.stdout.write(self.style.ERROR("No payment rules found for India."))
            return

        updated_count = 0

        for india_rule in india_rules:

            # Fetch matching rules from other countries
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
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully updated {updated_count} payment rules in other countries to match India."
        ))
