from django.db import models
from core.models import TimeStampedModel, Tenant

class Category(TimeStampedModel):
    """Ürün kategorileri"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    code = models.CharField(max_length=20, verbose_name="Kategori Kodu")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        unique_together = [['tenant', 'code']]
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Product(TimeStampedModel):
    """Ürün modeli"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    
    code = models.CharField(max_length=50, verbose_name="Ürün Kodu", db_index=True)
    name = models.CharField(max_length=255, verbose_name="Ürün Adı")
    barcode = models.CharField(max_length=50, blank=True, db_index=True)
    
    unit = models.CharField(max_length=20, default='ADET', verbose_name="Birim")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Temel Fiyat")
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20, verbose_name="KDV Oranı %")
    
    stock_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Stok Miktarı")
    min_stock_level = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name="Min Stok")
    
    is_active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        unique_together = [['tenant', 'code']]
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['tenant', 'code']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class DealerPrice(TimeStampedModel):
    """Bayiye özel fiyat listesi"""
    dealer = models.ForeignKey('accounts.Dealer', on_delete=models.CASCADE, related_name='special_prices')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='dealer_prices')
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Özel Fiyat")
    valid_from = models.DateField(verbose_name="Geçerlilik Başlangıç")
    valid_until = models.DateField(null=True, blank=True, verbose_name="Geçerlilik Bitiş")
    
    class Meta:
        db_table = 'dealer_prices'
        verbose_name = 'Bayi Özel Fiyat'
        verbose_name_plural = 'Bayi Özel Fiyatlar'
        unique_together = [['dealer', 'product', 'valid_from']]
        indexes = [
            models.Index(fields=['dealer', 'product', 'valid_from']),
        ]
    
    def __str__(self):
        return f"{self.dealer.code} - {self.product.code}: {self.price}"


class ProductOptionGroup(TimeStampedModel):
    """Ürün opsiyon grubu (örn. Acı Seviyesi)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='option_groups')
    name = models.CharField(max_length=100, verbose_name="Grup Adı")
    is_required = models.BooleanField(default=True, verbose_name="Zorunlu Mu")
    allow_multiple = models.BooleanField(default=False, verbose_name="Çoklu Seçim")
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'product_option_groups'
        verbose_name = 'Ürün Opsiyon Grubu'
        verbose_name_plural = 'Ürün Opsiyon Grupları'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.product.code} — {self.name}"


class ProductOptionItem(TimeStampedModel):
    """Opsiyon grubu içindeki seçenek (örn. Acılı)"""
    group = models.ForeignKey(ProductOptionGroup, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100, verbose_name="Seçenek Adı")
    price_delta = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Fiyat Farkı"
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'product_option_items'
        verbose_name = 'Ürün Opsiyon Seçeneği'
        verbose_name_plural = 'Ürün Opsiyon Seçenekleri'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.group.name}: {self.name}"
