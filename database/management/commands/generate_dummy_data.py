import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from faker import Faker
from database.models import Tenant, InvestmentScheme, StaffAPI, Contribution, Membership

class Command(BaseCommand):
    help = 'Generate dummy data for 50 members with contributions'

    def handle(self, *args, **options):
        fake = Faker()

        # Create Tenant
        tenant, _ = Tenant.objects.get_or_create(
            id=2,
            defaults={
                'name':"FCK Ghana Ltd",
                'api_endpoint_member': 'http://127.0.0.1:8080/api/staff',
                'api_endpoint_contribution': 'https://127.0.0.1:8080/api/contributions/',
                'tel_number': fake.random_int(min=1000000000, max=9999999999),
                'email': 'admin@samplecorp.com',
                'address': fake.address()
            }
        )

        # Create only one Investment Scheme with ID 4
        scheme, _ = InvestmentScheme.objects.update_or_create(
            id=4,
            defaults={
                'code': '442',
                'name': 'Retirement Plan',
                'tenant': tenant,
                'approved': True
            }
        )

        banks = [
            'Ghana Commercial Bank', 'Ecobank Ghana', 'Standard Chartered Bank',
            'Zenith Bank Ghana', 'Fidelity Bank Ghana', 'CAL Bank',
            'ADB Bank', 'Prudential Bank', 'Universal Merchant Bank'
        ]

        fund_types = ['pension', 'provident', 'gratuity', 'savings']

        staff_members = []

        for i in range(1, 51):
            staff_number = f"{i:04d}"

            if not StaffAPI.objects.filter(staff_number=staff_number).exists():
                staff = StaffAPI.objects.create(
                    tenant=tenant,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    staff_number=staff_number,
                    status=random.choice(['active', 'active', 'active', 'inactive']),  # 75% active
                    fund_type=random.choice(fund_types),
                    subscription_date=fake.date_between(start_date='-3y', end_date='today'),
                    bank_name=random.choice(banks),
                    bank_branch=fake.city(),
                    bank_account_number=fake.random_int(min=1000000000, max=9999999999),
                )

                # Assign the only investment scheme
                staff.investment_scheme.set([scheme])
                staff_members.append(staff)

        # Generate Contributions for each staff member
        for staff in staff_members:
            # Only one contribution per staff member
            contribution_date = datetime.now().date()

            base_employee = Decimal(random.uniform(500, 2000)).quantize(Decimal('0.01'))
            base_employer = (base_employee * Decimal('0.5')).quantize(Decimal('0.01'))

            retro_employee = Decimal(random.uniform(0, 200)).quantize(Decimal('0.01')) if random.random() > 0.7 else Decimal('0')
            retro_employer = (retro_employee * Decimal('0.5')).quantize(Decimal('0.01')) if retro_employee > 0 else Decimal('0')

            Contribution.objects.create(
                investment_scheme=scheme,
                member=staff,
                contribution_date=contribution_date,
                employee_amount=base_employee,
                employer_amount=base_employer,
                retro_employee_amount=retro_employee,
                retro_employer_amount=retro_employer,
                approved_contribution=random.choice([True, True, True])  # Mostly approved
            )

        # Generate Memberships
        for staff in staff_members:
            Membership.objects.get_or_create(
                tenant=tenant,
                staff=staff,
                scheme=scheme,
                defaults={
                    'total_earnings': Decimal(random.uniform(1000, 10000)).quantize(Decimal('0.01')),
                    'estimated_profit': Decimal(random.uniform(500, 5000)).quantize(Decimal('0.01')),
                }
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated dummy data for {len(staff_members)} staff members'
            )
        )
