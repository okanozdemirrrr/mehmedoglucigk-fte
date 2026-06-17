from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.services.notifications import notify_dealer, notify_tenant_distributors
from .models import Order


@receiver(pre_save, sender=Order)
def capture_order_status_for_push(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_status = (
                Order.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
            )
        except Exception:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Order)
def order_push_notifications(sender, instance, created, **kwargs):
    previous = getattr(instance, '_previous_status', None)
    dealer_name = instance.dealer.name if instance.dealer_id else 'Bayi'
    order_data = {
        'order_id': str(instance.id),
        'order_number': instance.order_number,
        'type': 'order_update',
    }

    # Tetikleyici 1: Yeni sipariş (PENDING)
    if created and instance.status == 'PENDING':
        notify_tenant_distributors(
            instance.tenant,
            title='Yeni Sipariş Geldi!',
            body=f'{dealer_name} yeni bir sipariş oluşturdu.',
            data={**order_data, 'type': 'new_order'},
        )
        return

    if created or previous == instance.status:
        return

    # Tetikleyici 2: Onay / hazırlık / yola çıkış → bayiye bildir
    shipped_statuses = {'ON_THE_WAY', 'APPROVED', 'PREPARING'}
    if instance.status in shipped_statuses and previous not in shipped_statuses:
        notify_dealer(
            instance.dealer,
            title='Siparişiniz Yola Çıktı',
            body='Siparişiniz yola çıkmıştır, kuryemiz yaklaşıyor.',
            data={**order_data, 'type': 'order_shipped', 'status': instance.status},
        )

    # Tetikleyici 3: Teslim onayı → dağıtıcıya bildir
    if instance.status == 'DELIVERED' and previous != 'DELIVERED':
        notify_tenant_distributors(
            instance.tenant,
            title='Teslimat Onaylandı',
            body=f'{dealer_name} siparişi teslim aldığını onayladı. Tutar cariye işlendi.',
            data={**order_data, 'type': 'order_delivered'},
        )
