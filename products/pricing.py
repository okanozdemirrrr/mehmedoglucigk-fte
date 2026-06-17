from decimal import Decimal

from django.db.models import Q
from django.utils import timezone


def get_effective_price(dealer, product, as_of=None) -> Decimal:
    """Bayi için geçerli fiyat: dealer_prices varsa onu, yoksa base_price."""
    from .models import DealerPrice

    if as_of is None:
        as_of = timezone.localdate()

    dealer_price = (
        DealerPrice.objects.filter(
            dealer=dealer,
            product=product,
            valid_from__lte=as_of,
        )
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=as_of))
        .order_by('-valid_from')
        .first()
    )
    if dealer_price:
        return dealer_price.price
    return product.base_price
