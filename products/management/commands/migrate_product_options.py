from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from core.models import Tenant
from products.models import Product, Category, ProductOptionGroup, ProductOptionItem

LEGACY_CODES = {'CK-001', 'CK-002', 'CK-003'}


class Command(BaseCommand):
    help = 'Ayrı çiğköfte ürünlerini tek üründe birleştirir ve opsiyon grupları oluşturur.'

    def handle(self, *args, **options):
        for tenant in Tenant.objects.all():
            self.migrate_tenant(tenant)

    @transaction.atomic
    def migrate_tenant(self, tenant):
        self.stdout.write(f'Tenant: {tenant.name}')

        category, _ = Category.objects.get_or_create(
            tenant=tenant,
            code='CK',
            defaults={'name': 'Çiğköfte', 'is_active': True},
        )

        legacy_products = Product.objects.filter(tenant=tenant, is_active=True).filter(
            Q(code__in=LEGACY_CODES) | Q(name__icontains='çiğköfte')
        ).exclude(code='CK-MAIN')

        unified, created = Product.objects.get_or_create(
            tenant=tenant,
            code='CK-MAIN',
            defaults={
                'category': category,
                'name': 'Çiğköfte',
                'unit': 'KG',
                'base_price': Decimal('120.00'),
                'vat_rate': Decimal('20.00'),
                'stock_quantity': Decimal('0'),
                'is_active': True,
                'description': 'Ana çiğköfte ürünü — acı seviyesi opsiyon ile seçilir.',
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  + CK-MAIN oluşturuldu'))

        if legacy_products.exists():
            total_stock = sum(p.stock_quantity for p in legacy_products)
            unified.stock_quantity = max(unified.stock_quantity, total_stock)
            unified.save(update_fields=['stock_quantity', 'updated_at'])

        spice_group, _ = ProductOptionGroup.objects.get_or_create(
            product=unified,
            name='Acı Seviyesi',
            defaults={'is_required': True, 'allow_multiple': False, 'sort_order': 1},
        )
        for sort_order, name in enumerate(['Acılı', 'Acısız', 'Orta Acı'], start=1):
            ProductOptionItem.objects.get_or_create(
                group=spice_group,
                name=name,
                defaults={
                    'price_delta': Decimal('0'),
                    'sort_order': sort_order,
                    'is_active': True,
                },
            )

        extras_group, _ = ProductOptionGroup.objects.get_or_create(
            product=unified,
            name='Ekstralar',
            defaults={'is_required': False, 'allow_multiple': True, 'sort_order': 2},
        )
        extras = [
            ('Ekstra Lavaş', Decimal('5.00')),
            ('Nar Ekşisi Sos', Decimal('3.00')),
        ]
        for sort_order, (name, delta) in enumerate(extras, start=1):
            ProductOptionItem.objects.get_or_create(
                group=extras_group,
                name=name,
                defaults={
                    'price_delta': delta,
                    'sort_order': sort_order,
                    'is_active': True,
                },
            )

        deactivated = legacy_products.update(is_active=False)
        self.stdout.write(f'  {deactivated} eski ürün pasifleştirildi.')
        self.stdout.write(self.style.SUCCESS(f'  {tenant.name} tamamlandı.'))
