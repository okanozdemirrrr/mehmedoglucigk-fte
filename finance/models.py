from django.db import models
from core.models import TimeStampedModel, Tenant
from accounts.models import Dealer
from orders.models import Order

class CariAccount(TimeStampedModel):
    """Cari hesap hareketleri"""
    TRANSACTION_TYPES = [
        ('INVOICE', 'Fatura'),
        ('PAYMENT', 'Tahsilat'),
        ('RETURN', 'İade'),
        ('ADJUSTMENT', 'Düzeltme'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='cari_transactions')
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT, related_name='cari_transactions')
    
    transaction_date = models.DateTimeField(auto_now_add=True, db_index=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, db_index=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tutar")
    description = models.TextField(verbose_name="Açıklama")
    
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='cari_entries')
    invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='cari_entries')
    
    class Meta:
        db_table = 'cari_accounts'
        verbose_name = 'Cari Hesap'
        verbose_name_plural = 'Cari Hesaplar'
        indexes = [
            models.Index(fields=['tenant', 'dealer', 'transaction_date']),
            models.Index(fields=['dealer', 'transaction_type']),
        ]
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.dealer.code} - {self.get_transaction_type_display()}: {self.amount}"

class Invoice(TimeStampedModel):
    """E-Fatura modeli"""
    STATUS_CHOICES = [
        ('DRAFT', 'Taslak'),
        ('PENDING', 'GİB\'e Gönderilecek'),
        ('SENT', 'GİB\'e Gönderildi'),
        ('APPROVED', 'Onaylandı'),
        ('REJECTED', 'Reddedildi'),
        ('CANCELLED', 'İptal'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invoices')
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT, related_name='invoices')
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name='invoice')
    
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    invoice_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(verbose_name="Vade Tarihi")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', db_index=True)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Ara Toplam")
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="KDV")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Toplam")
    
    gib_uuid = models.CharField(max_length=100, blank=True, verbose_name="GİB UUID")
    gib_response = models.JSONField(null=True, blank=True, verbose_name="GİB Yanıtı")
    gib_sent_at = models.DateTimeField(null=True, blank=True)
    
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturalar'
        indexes = [
            models.Index(fields=['tenant', 'status', 'invoice_date']),
            models.Index(fields=['dealer', 'status']),
        ]
        ordering = ['-invoice_date']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.dealer.name}"
    
    def send_to_gib(self):
        """
        E-Faturayı GİB'e gönder
        MONITORING: Hata durumunda Sentry'ye bildir
        """
        from .services import EFaturaService
        from core.monitoring import monitor_critical_operation, alert_failed_invoice
        
        if self.status not in ['DRAFT', 'PENDING']:
            raise ValueError('Sadece taslak veya bekleyen faturalar gönderilebilir')
        
        service = EFaturaService(self.tenant)
        
        @monitor_critical_operation('E-Fatura Gönderimi')
        def _send():
            return service.send_invoice(self)
        
        try:
            result = _send()
            self.status = 'SENT'
            self.gib_uuid = result.get('uuid')
            self.gib_response = result
            from django.utils import timezone
            self.gib_sent_at = timezone.now()
            self.save()
            
            CariAccount.objects.create(
                tenant=self.tenant,
                dealer=self.dealer,
                transaction_type='INVOICE',
                amount=self.total_amount,
                description=f'Fatura: {self.invoice_number}',
                order=self.order,
                invoice=self
            )
            return True
        
        except Exception as e:
            self.status = 'REJECTED'
            self.gib_response = {'error': str(e)}
            self.save()
            
            alert_failed_invoice(self, e)
            raise
