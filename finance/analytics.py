from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from orders.models import Order
from finance.models import CariAccount


def get_date_range(date_filter):
    today = timezone.localdate()
    if date_filter == 'today':
        start = today
    elif date_filter == 'this_week':
        start = today - timedelta(days=today.weekday())
    else:
        start = today.replace(day=1)
    return start, today


def _unpaid_delivered_receivable(tenant):
    """
    Ödenmemiş teslim edilmiş siparişlerin toplam alacağı.
    Cari bakiye pozitifse cari üzerinden; aksi halde DELIVERED sipariş toplamından hesaplanır.
    """
    cari_balance = CariAccount.objects.filter(tenant=tenant).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    if cari_balance > 0:
        return cari_balance

    return Order.objects.filter(
        tenant=tenant,
        status='DELIVERED',
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')


def build_dashboard_payload(tenant, date_filter='this_month'):
    if tenant is None:
        return {
            'period': date_filter,
            'date_from': None,
            'date_to': None,
            'kpis': {
                'total_revenue': '0',
                'order_count': 0,
                'pending_orders': 0,
                'total_collection': '0',
                'total_receivables': '0',
            },
            'revenue_trend': [],
            'recent_activity': [],
        }

    start, end = get_date_range(date_filter)

    delivered_qs = Order.objects.filter(
        tenant=tenant,
        status='DELIVERED',
        order_date__date__gte=start,
        order_date__date__lte=end,
    )

    total_revenue = delivered_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    order_count = delivered_qs.count()
    pending_orders = Order.objects.filter(tenant=tenant, status='PENDING').count()

    collections = CariAccount.objects.filter(
        tenant=tenant,
        transaction_type='PAYMENT',
        transaction_date__date__gte=start,
        transaction_date__date__lte=end,
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    total_receivables = _unpaid_delivered_receivable(tenant)

    trend = list(
        delivered_qs.annotate(day=TruncDate('order_date'))
        .values('day')
        .annotate(amount=Sum('total_amount'), count=Count('id'))
        .order_by('day')
    )

    recent_orders = [
        {
            'type': 'order',
            'dealer_name': order.dealer.name,
            'dealer_code': order.dealer.code,
            'amount': str(order.total_amount),
            'description': order.order_number,
            'timestamp': order.order_date.isoformat(),
        }
        for order in delivered_qs.select_related('dealer').order_by('-order_date')[:20]
    ]

    recent_payments = [
        {
            'type': 'payment',
            'dealer_name': entry.dealer.name,
            'dealer_code': entry.dealer.code,
            'amount': str(abs(entry.amount)),
            'description': entry.description,
            'timestamp': entry.transaction_date.isoformat(),
        }
        for entry in CariAccount.objects.filter(
            tenant=tenant,
            transaction_type='PAYMENT',
            transaction_date__date__gte=start,
            transaction_date__date__lte=end,
        ).select_related('dealer').order_by('-transaction_date')[:20]
    ]

    recent_activity = sorted(
        recent_orders + recent_payments,
        key=lambda row: row['timestamp'],
        reverse=True,
    )[:30]

    return {
        'period': date_filter,
        'date_from': str(start),
        'date_to': str(end),
        'kpis': {
            'total_revenue': str(total_revenue),
            'order_count': order_count,
            'pending_orders': pending_orders,
            'total_collection': str(abs(collections)),
            'total_receivables': str(total_receivables),
        },
        'revenue_trend': [
            {
                'date': str(row['day']),
                'amount': str(row['amount'] or 0),
                'count': row['count'],
            }
            for row in trend
        ],
        'recent_activity': recent_activity,
    }
