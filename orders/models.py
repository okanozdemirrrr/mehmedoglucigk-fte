from django.db import models
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel, Tenant
from accounts.models import Dealer
from products.models import Product

class Order(TimeStampedModel):
    """Sipariş modeli"""
    STATUS_CHOICES = [
        ('DRAFT', 'Taslak'),
        ('PENDING', 'Onay Bekliyor'),
        ('APPROVED', 'Onaylandı'),
        ('PREPARING', 'Hazırlanıyor'),
        ('ON_THE_WAY', 'Yolda'),
        ('DELIVERED', 'Teslim Edildi'),
        ('CANCELLED', 'İptal'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='orders')
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT, related_name='orders')
    
    order_number = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Sipariş No")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Sipariş Tarihi")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', db_index=True)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Ara Toplam")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="İskonto")
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="KDV")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Toplam")
    
    notes = models.TextField(blank=True, verbose_name="Notlar")
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_orders')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Sipariş'
        verbose_name_plural = 'Siparişler'
        indexes = [
            models.Index(fields=['tenant', 'status', 'order_date']),
            models.Index(fields=['dealer', 'status']),
        ]
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.dealer.name}"

    def calculate_totals(self):
        """Sipariş toplamlarını hesapla"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.discount_amount = self.subtotal * (self.dealer.discount_rate / 100)
        self.vat_amount = sum(item.vat_amount for item in items)
        self.total_amount = self.subtotal - self.discount_amount + self.vat_amount
        self.save()
    
    def approve(self, user):
        """
        Siparişi onayla ve stokları düş
        CONCURRENCY SAFE: select_for_update ile race condition önlenir
        """
        from django.db import transaction
        
        if self.status != 'PENDING':
            raise ValidationError('Sadece bekleyen siparişler onaylanabilir')
        
        with transaction.atomic():
            # Tüm ürünleri kilitle (race condition önleme)
            for item in self.items.select_related('product'):
                product = Product.objects.select_for_update().get(id=item.product.id)
                
                if product.stock_quantity < item.quantity:
                    raise ValidationError(
                        f'{product.name} için yeterli stok yok. '
                        f'Mevcut: {product.stock_quantity}, İstenen: {item.quantity}'
                    )
                
                product.stock_quantity -= item.quantity
                product.save()
                
                # Stok uyarısı
                from core.monitoring import alert_low_stock
                alert_low_stock(product)
            
            self.status = 'PREPARING' # Prompt requirement: approve_and_invoice transitions to PREPARING
            self.approved_by = user
            from django.utils import timezone
            self.approved_at = timezone.now()
            self.save()

    def ship_order(self, user):
        if self.status != 'PREPARING':
            raise ValidationError('Sadece hazırlanan siparişler yola çıkarılabilir')
        self.status = 'ON_THE_WAY'
        self.save()

    def complete_delivery(self, user):
        if self.status != 'ON_THE_WAY':
            raise ValidationError('Sadece yoldaki siparişler teslim edilebilir')
        self.status = 'DELIVERED'
        self.save()

class OrderItem(TimeStampedModel):
    """Sipariş kalemi"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    
    quantity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Miktar")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Fiyat")
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="KDV %")
    
    line_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Satır Toplamı")
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="KDV Tutarı")
    selected_options = models.JSONField(default=list, blank=True, verbose_name="Seçilen Opsiyonlar")

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Sipariş Kalemi'
        verbose_name_plural = 'Sipariş Kalemleri'
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        self.vat_amount = self.line_total * (self.vat_rate / 100)
        super().save(*args, **kwargs)
    
    @property
    def options_display(self):
        if not self.selected_options:
            return ''
        return ', '.join(
            opt.get('option_name', '')
            for opt in self.selected_options
            if opt.get('option_name')
        )

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name}"
