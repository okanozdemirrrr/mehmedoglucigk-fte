from django.contrib import admin
from .models import Category, Product, DealerPrice, ProductOptionGroup, ProductOptionItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'tenant', 'parent', 'is_active']
    list_filter = ['is_active', 'tenant']
    search_fields = ['code', 'name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'base_price', 'stock_quantity', 'is_active']
    list_filter = ['is_active', 'tenant', 'category']
    search_fields = ['code', 'name', 'barcode']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DealerPrice)
class DealerPriceAdmin(admin.ModelAdmin):
    list_display = ['dealer', 'product', 'price', 'valid_from', 'valid_until']
    list_filter = ['dealer', 'valid_from']
    search_fields = ['dealer__code', 'product__code']


class ProductOptionItemInline(admin.TabularInline):
    model = ProductOptionItem
    extra = 1


@admin.register(ProductOptionGroup)
class ProductOptionGroupAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'is_required', 'allow_multiple', 'sort_order']
    list_filter = ['is_required', 'allow_multiple']
    inlines = [ProductOptionItemInline]
