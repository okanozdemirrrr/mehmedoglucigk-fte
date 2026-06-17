from django.db import models
from core.models import TimeStampedModel, Tenant
from orders.models import Order

class Vehicle(TimeStampedModel):
    """Araç modeli"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='vehicles')
    
    plate_number = models.CharField(max_length=20, verbose_name="Plaka")
    brand = models.CharField(max_length=50, verbose_name="Marka")
    model = models.CharField(max_length=50, verbose_name="Model")
    capacity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Kapasite (kg)")
    
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        db_table = 'vehicles'
        verbose_name = 'Araç'
        verbose_name_plural = 'Araçlar'
        unique_together = [['tenant', 'plate_number']]
    
    def __str__(self):
        return f"{self.plate_number} - {self.brand} {self.model}"

class Route(TimeStampedModel):
    """Sevkiyat rotası"""
    STATUS_CHOICES = [
        ('PLANNED', 'Planlandı'),
        ('IN_PROGRESS', 'Yolda'),
        ('COMPLETED', 'Tamamlandı'),
        ('CANCELLED', 'İptal'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='routes')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='routes')
    driver = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='routes')
    
    route_number = models.CharField(max_length=50, unique=True, db_index=True)
    route_date = models.DateField(verbose_name="Sevkiyat Tarihi", db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED', db_index=True)
    
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'routes'
        verbose_name = 'Rota'
        verbose_name_plural = 'Rotalar'
        indexes = [
            models.Index(fields=['tenant', 'route_date', 'status']),
        ]
        ordering = ['-route_date']
    
    def __str__(self):
        return f"{self.route_number} - {self.route_date}"


class Shipment(TimeStampedModel):
    """Sevkiyat detayı"""
    STATUS_CHOICES = [
        ('PENDING', 'Bekliyor'),
        ('LOADED', 'Yüklendi'),
        ('IN_TRANSIT', 'Yolda'),
        ('DELIVERED', 'Teslim Edildi'),
        ('RETURNED', 'İade'),
    ]
    
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='shipments')
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name='shipment')
    
    sequence = models.IntegerField(verbose_name="Sıra", default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    
    loaded_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    recipient_name = models.CharField(max_length=100, blank=True, verbose_name="Teslim Alan")
    recipient_signature = models.ImageField(upload_to='signatures/', null=True, blank=True)
    delivery_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'shipments'
        verbose_name = 'Sevkiyat'
        verbose_name_plural = 'Sevkiyatlar'
        ordering = ['route', 'sequence']
    
    def __str__(self):
        return f"{self.route.route_number} - {self.order.order_number}"
