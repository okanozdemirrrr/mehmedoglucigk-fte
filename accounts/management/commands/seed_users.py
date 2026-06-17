import os
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User, Dealer
from core.models import Tenant

DEFAULT_USERS = [
    {
        'email': 'admin@mergen.com',
        'password_env': 'SEED_ADMIN_PASSWORD',
        'default_password': '123456',
        'role': 'SUPERADMIN',
        'is_superuser': True,
        'is_staff': True,
        'dealer_code': None,
    },
    {
        'email': 'bayi@mergen.com',
        'password_env': 'SEED_DEALER_PASSWORD',
        'default_password': '123456',
        'role': 'DEALER',
        'is_superuser': False,
        'is_staff': False,
        'dealer_code': 'BY-001',
    },
]


class Command(BaseCommand):
    help = 'Tüm giriş hesaplarını users tablosuna yazar (tek kaynak).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            help='Tüm seed kullanıcıları için ortak şifre (ortam değişkenlerini geçersiz kılar)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        override_password = options.get('password')

        tenant, created = Tenant.objects.get_or_create(
            slug='merkez',
            defaults={
                'name': 'Mergen Merkez',
                'tax_office': 'Kadıköy',
                'tax_number': '1234567890',
                'address': 'İstanbul',
                'phone': '02160000000',
                'email': 'info@mergen.com',
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Tenant oluşturuldu: Mergen Merkez'))

        dealer, dealer_created = Dealer.objects.get_or_create(
            tenant=tenant,
            code='BY-001',
            defaults={
                'name': 'Mehmet Usta Çiğköfte',
                'tax_office': 'Kadıköy',
                'tax_number': '9876543210',
                'address': 'Caferağa Mah. İstanbul',
                'city': 'İstanbul',
                'district': 'Kadıköy',
                'phone': '05321234567',
                'email': 'iletisim@mehmetusta.com',
                'credit_limit': Decimal('50000.00'),
                'discount_rate': Decimal('5.00'),
                'is_active': True,
            },
        )
        if dealer_created:
            self.stdout.write(self.style.SUCCESS(f'Bayi oluşturuldu: {dealer.name}'))

        for spec in DEFAULT_USERS:
            password = override_password or os.environ.get(
                spec['password_env'],
                spec['default_password'],
            )
            email = spec['email'].lower()

            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    'tenant': tenant,
                    'role': spec['role'],
                    'is_staff': spec['is_staff'],
                    'is_superuser': spec['is_superuser'],
                    'is_active': True,
                },
            )

            if spec['dealer_code']:
                user.dealer = dealer
            else:
                user.dealer = None

            user.tenant = tenant
            user.role = spec['role']
            user.is_staff = spec['is_staff']
            user.is_superuser = spec['is_superuser']
            user.is_active = True
            user.set_password(password)
            user.save()

            action = 'Oluşturuldu' if user_created else 'Güncellendi'
            self.stdout.write(
                self.style.SUCCESS(
                    f'{action}: {email} ({spec["role"]}) — şifre users tablosunda hash olarak saklandı'
                )
            )

        self.stdout.write('')
        self.stdout.write('Giriş bilgileri yalnızca users tablosundadır.')
        self.stdout.write('Admin: admin@mergen.com')
        self.stdout.write('Bayi:  bayi@mergen.com')
        if override_password:
            self.stdout.write(f'Şifre:  (komut satırından verildi)')
        else:
            self.stdout.write('Şifre:  SEED_ADMIN_PASSWORD / SEED_DEALER_PASSWORD veya varsayılan 123456')
