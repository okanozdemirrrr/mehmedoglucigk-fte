from decimal import Decimal

from django.core.exceptions import ValidationError

from .models import ProductOptionGroup


def validate_and_resolve_options(product, selected_options):
    """
    Seçilen opsiyonları doğrular, normalize edilmiş liste ve toplam fiyat farkını döner.
    """
    if selected_options is None:
        selected_options = []

    groups = ProductOptionGroup.objects.filter(product=product).prefetch_related('items')
    group_map = {g.id: g for g in groups}

    option_by_id = {}
    for group in groups:
        for item in group.items.filter(is_active=True):
            option_by_id[item.id] = (group, item)

    selections_by_group = {}
    for raw in selected_options:
        option_id = raw.get('option_id')
        if option_id is None:
            continue
        option_id = int(option_id)
        if option_id not in option_by_id:
            raise ValidationError(f'Geçersiz opsiyon ID: {option_id}')
        group, item = option_by_id[option_id]
        selections_by_group.setdefault(group.id, []).append(item)

    for group in groups:
        selected = selections_by_group.get(group.id, [])
        if group.is_required and not selected:
            raise ValidationError(f'"{group.name}" seçimi zorunludur.')
        if not group.allow_multiple and len(selected) > 1:
            raise ValidationError(f'"{group.name}" için yalnızca bir seçim yapılabilir.')

    validated = []
    options_delta = Decimal('0')
    for group_id, items in selections_by_group.items():
        group = group_map[group_id]
        for item in items:
            validated.append({
                'group_id': group.id,
                'group_name': group.name,
                'option_id': item.id,
                'option_name': item.name,
                'price_delta': str(item.price_delta),
            })
            options_delta += item.price_delta

    return validated, options_delta
