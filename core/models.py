from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """Tüm modeller için ortak zaman damgası alanları"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Tenant(TimeStampedModel):
    """Multi-tenant yapı için ana firma/müşteri modeli"""
    name = models.CharField(max_length=255, verbose_name="Firma Adı")
    slug = models.SlugField(unique=True, db_index=True)
    tax_office = models.CharField(max_length=100, verbose_name="Vergi Dairesi")
    tax_number = models.CharField(max_length=20, unique=True, verbose_name="Vergi No")
    address = models.TextField(verbose_name="Adres")
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    
    is_active = models.BooleanField(default=True, db_index=True)
    subscription_start = models.DateField(default=timezone.now)
    subscription_end = models.DateField(null=True, blank=True)
    
    efatura_username = models.CharField(max_length=100, blank=True)
    efatura_password = models.CharField(max_length=255, blank=True)
    efatura_provider = models.CharField(max_length=50, default='parasut')
    
    class Meta:
        db_table = 'tenants'
        verbose_name = 'Müşteri Firma'
        verbose_name_plural = 'Müşteri Firmalar'
    
    def __str__(self):
        return self.name
