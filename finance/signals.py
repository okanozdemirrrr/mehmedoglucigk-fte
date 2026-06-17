from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from orders.models import Order
from finance.cari_service import record_delivery_debt


@receiver(pre_save, sender=Order)
def capture_previous_order_status(sender, instance, **kwargs):
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
def order_delivered_cari_entry(sender, instance, created, **kwargs):
    previous_status = getattr(instance, '_previous_status', None)
    became_delivered = instance.status == 'DELIVERED' and (
        created or previous_status != 'DELIVERED'
    )
    if became_delivered:
        record_delivery_debt(instance)
