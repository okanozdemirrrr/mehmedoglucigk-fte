from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from products.models import Product
from products.pricing import get_effective_price
from products.option_validation import validate_and_resolve_options

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    options_display = serializers.CharField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity',
            'unit_price', 'vat_rate', 'line_total', 'vat_amount',
            'selected_options', 'options_display',
        ]
        read_only_fields = [
            'id', 'line_total', 'vat_amount', 'unit_price', 'vat_rate', 'options_display',
        ]


class OrderItemWriteSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True))
    quantity = serializers.DecimalField(max_digits=10, decimal_places=3, min_value=0.001)
    selected_options = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list,
    )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_write = OrderItemWriteSerializer(many=True, write_only=True, required=False)
    dealer_name = serializers.CharField(source='dealer.name', read_only=True)
    dealer_code = serializers.CharField(source='dealer.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'dealer', 'dealer_name', 'dealer_code',
            'order_date', 'status', 'status_display',
            'subtotal', 'discount_amount', 'vat_amount', 'total_amount',
            'notes', 'items', 'items_write',
        ]
        read_only_fields = [
            'id', 'order_number', 'order_date', 'subtotal',
            'discount_amount', 'vat_amount', 'total_amount', 'dealer', 'tenant',
        ]

    def to_internal_value(self, data):
        if isinstance(data, dict) and 'items' in data and 'items_write' not in data:
            data = {**data, 'items_write': data['items']}
        return super().to_internal_value(data)

    def validate(self, attrs):
        if not attrs.get('items_write'):
            raise serializers.ValidationError({'items': 'En az bir sipariş kalemi gerekli.'})
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items_write')
        self._items_data = items_data
        return Order(**validated_data)

    def save(self, **kwargs):
        items_data = getattr(self, '_items_data', None)
        order = super().save(**kwargs)

        if items_data is not None and not order.items.exists():
            dealer = order.dealer
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                raw_options = item_data.get('selected_options', [])

                try:
                    validated_options, options_delta = validate_and_resolve_options(
                        product, raw_options
                    )
                except DjangoValidationError as exc:
                    raise serializers.ValidationError({'items': exc.messages})

                unit_price = get_effective_price(dealer, product) + options_delta

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    vat_rate=product.vat_rate,
                    selected_options=validated_options,
                )

            order.calculate_totals()

        return order
