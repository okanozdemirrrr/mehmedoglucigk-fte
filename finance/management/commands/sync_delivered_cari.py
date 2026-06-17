from django.core.management.base import BaseCommand

from core.models import Tenant
from finance.cari_service import sync_delivered_orders_cari


class Command(BaseCommand):
    help = 'Teslim edilmiş siparişler için eksik cari hesap kayıtlarını oluşturur'

    def add_arguments(self, parser):
        parser.add_argument('--tenant-id', type=int, default=None)

    def handle(self, *args, **options):
        tenant_id = options.get('tenant_id')
        tenant = Tenant.objects.get(pk=tenant_id) if tenant_id else None
        created = sync_delivered_orders_cari(tenant)
        self.stdout.write(self.style.SUCCESS(f'{created} cari kaydı oluşturuldu.'))
