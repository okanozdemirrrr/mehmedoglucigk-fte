from decimal import Decimal

from django.db import transaction

from finance.models import CariAccount


def record_delivery_debt(order):
    """
    Teslim edilen sipariş tutarını bayi cari hesabına borç (alacak) olarak yazar.
    Aynı sipariş için tekrar kayıt oluşturmaz.
    """
    if order.status != 'DELIVERED':
        return None

    if order.cari_entries.filter(transaction_type='INVOICE').exists():
        return order.cari_entries.filter(transaction_type='INVOICE').first()

    amount = order.total_amount or Decimal('0')
    if amount <= 0:
        return None

    with transaction.atomic():
        if order.cari_entries.filter(transaction_type='INVOICE').exists():
            return order.cari_entries.filter(transaction_type='INVOICE').first()

        return CariAccount.objects.create(
            tenant=order.tenant,
            dealer=order.dealer,
            transaction_type='INVOICE',
            amount=amount,
            description=f'Sipariş Teslimatı - {order.order_number}',
            order=order,
        )


def record_payment(dealer, tenant, amount, method='Nakit/EFT'):
    """Bayiden tahsilat — cari borcu düşürür (negatif tutar)."""
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValueError('Tahsilat tutarı 0\'dan büyük olmalıdır.')

    return CariAccount.objects.create(
        tenant=tenant,
        dealer=dealer,
        transaction_type='PAYMENT',
        amount=-amount,
        description=f'Tahsilat ({method})',
    )


def sync_delivered_orders_cari(tenant=None):
    """Mevcut DELIVERED siparişler için eksik cari kayıtlarını tamamlar."""
    from orders.models import Order

    qs = Order.objects.filter(status='DELIVERED').select_related('tenant', 'dealer')
    if tenant is not None:
        qs = qs.filter(tenant=tenant)

    created = 0
    for order in qs:
        before = order.cari_entries.filter(transaction_type='INVOICE').count()
        record_delivery_debt(order)
        after = order.cari_entries.filter(transaction_type='INVOICE').count()
        if after > before:
            created += 1
    return created
