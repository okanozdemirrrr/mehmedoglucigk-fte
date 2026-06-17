from rest_framework import serializers

from .models import Product, Category, DealerPrice, ProductOptionGroup, ProductOptionItem
from .pricing import get_effective_price


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'parent', 'is_active']
        read_only_fields = ['id']


class ProductOptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOptionItem
        fields = ['id', 'name', 'price_delta', 'is_active', 'sort_order']
        read_only_fields = ['id']


class ProductOptionGroupSerializer(serializers.ModelSerializer):
    items = ProductOptionItemSerializer(many=True, read_only=True)

    class Meta:
        model = ProductOptionGroup
        fields = ['id', 'name', 'is_required', 'allow_multiple', 'sort_order', 'items']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'code', 'name', 'barcode', 'category', 'category_name',
            'unit', 'base_price', 'vat_rate', 'stock_quantity',
            'min_stock_level', 'is_active', 'description',
        ]
        read_only_fields = ['id', 'stock_quantity']


class ProductCatalogSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    effective_price = serializers.SerializerMethodField()
    option_groups = ProductOptionGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'code', 'name', 'barcode', 'category', 'category_name',
            'unit', 'base_price', 'effective_price', 'vat_rate',
            'stock_quantity', 'min_stock_level', 'is_active', 'description',
            'option_groups',
        ]

    def get_effective_price(self, obj):
        dealer = self.context.get('dealer')
        if not dealer:
            return str(obj.base_price)
        return str(get_effective_price(dealer, obj))


class DealerPriceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    dealer_name = serializers.CharField(source='dealer.name', read_only=True)
    dealer_code = serializers.CharField(source='dealer.code', read_only=True)

    class Meta:
        model = DealerPrice
        fields = [
            'id', 'dealer', 'dealer_name', 'dealer_code',
            'product', 'product_name', 'price', 'valid_from', 'valid_until',
        ]
        read_only_fields = ['id']
