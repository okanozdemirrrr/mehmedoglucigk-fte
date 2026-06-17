"""
E-Fatura Entegrasyon Testleri
GİB senaryoları: Başarılı gönderim, timeout, iptal, iade
"""
import pytest
from unittest.mock import patch, Mock
from datetime import date, timedelta
from finance.models import Invoice, CariAccount
from finance.services import EFaturaService

@pytest.mark.django_db
class TestEFaturaIntegration:
    
    @patch('finance.services.requests.post')
    def test_successful_invoice_send(self, mock_post, tenant, dealer, admin_user):
        """Başarılı fatura gönderimi"""
        from orders.models import Order, OrderItem
        from products.models import Product, Category
        
        # Ürün ve sipariş hazırla
        category = Category.objects.create(tenant=tenant, code="KAT", name="Test")
        product = Product.objects.create(
            tenant=tenant, category=category, code="URN001",
            name="Test Ürün", base_price=100, vat_rate=20, stock_quantity=50
        )
        
        order = Order.objects.create(
            tenant=tenant, dealer=dealer, order_number="ORD-001",
            status='APPROVED', total_amount=120
        )
        
        OrderItem.objects.create(
            order=order, product=product, quantity=1,
            unit_price=100, vat_rate=20
        )
        
        # Fatura oluştur
        invoice = Invoice.objects.create(
            tenant=tenant,
            dealer=dealer,
            order=order,
            invoice_number="INV-001",
            due_date=date.today() + timedelta(days=30),
            subtotal=100,
            vat_amount=20,
            total_amount=120,
            status='PENDING'
        )
        
        # Mock GİB response
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {
                'uuid': '550e8400-e29b-41d4-a716-446655440000',
                'status': 'success'
            }
        )
        
        # Faturayı gönder
        invoice.send_to_gib()
        
        # Kontroller
        invoice.refresh_from_db()
        assert invoice.status == 'SENT'
        assert invoice.gib_uuid == '550e8400-e29b-41d4-a716-446655440000'
        assert invoice.gib_sent_at is not None
        
        # Cari kayıt oluşturuldu mu?
        cari = CariAccount.objects.filter(invoice=invoice).first()
        assert cari is not None
        assert cari.amount == 120
        assert cari.transaction_type == 'INVOICE'
    
    @patch('finance.services.requests.post')
    def test_gib_timeout_rollback(self, mock_post, tenant, dealer):
        """GİB timeout durumunda rollback"""
        from orders.models import Order
        
        order = Order.objects.create(
            tenant=tenant, dealer=dealer, order_number="ORD-002",
            status='APPROVED', total_amount=100
        )
        
        invoice = Invoice.objects.create(
            tenant=tenant, dealer=dealer, order=order,
            invoice_number="INV-002",
            due_date=date.today() + timedelta(days=30),
            total_amount=100,
            status='PENDING'
        )
        
        # Mock timeout
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        # Gönderim başarısız olmalı
        with pytest.raises(Exception) as exc_info:
            invoice.send_to_gib()
        
        assert "zaman aşımı" in str(exc_info.value).lower()
        
        # Fatura durumu REJECTED olmalı
        invoice.refresh_from_db()
        assert invoice.status == 'REJECTED'
        assert 'error' in invoice.gib_response
        
        # Cari kayıt OLUŞTURULMAMALI
        cari_count = CariAccount.objects.filter(invoice=invoice).count()
        assert cari_count == 0, "Timeout durumunda cari kayıt oluşturulmamalı!"
    
    def test_invoice_cancellation_within_8_days(self, tenant, dealer):
        """8 gün içinde fatura iptali (Mevzuat kuralı)"""
        from orders.models import Order
        from django.utils import timezone
        
        order = Order.objects.create(
            tenant=tenant, dealer=dealer, order_number="ORD-003",
            status='APPROVED', total_amount=100
        )
        
        invoice = Invoice.objects.create(
            tenant=tenant, dealer=dealer, order=order,
            invoice_number="INV-003",
            due_date=date.today() + timedelta(days=30),
            total_amount=100,
            status='SENT',
            gib_uuid='test-uuid'
        )
        
        # 7 gün önce gönderilmiş gibi ayarla
        invoice.gib_sent_at = timezone.now() - timedelta(days=7)
        invoice.save()
        
        # İptal edilebilir mi kontrol et
        from finance.services import EFaturaService
        service = EFaturaService(tenant)
        
        can_cancel = service.can_cancel_invoice(invoice)
        assert can_cancel is True, "7 gün içinde iptal edilebilmeli"
    
    def test_invoice_cancellation_after_8_days(self, tenant, dealer):
        """8 gün sonra fatura iptal edilemez, iade faturası gerekir"""
        from orders.models import Order
        from django.utils import timezone
        
        order = Order.objects.create(
            tenant=tenant, dealer=dealer, order_number="ORD-004",
            status='APPROVED', total_amount=100
        )
        
        invoice = Invoice.objects.create(
            tenant=tenant, dealer=dealer, order=order,
            invoice_number="INV-004",
            due_date=date.today() + timedelta(days=30),
            total_amount=100,
            status='SENT',
            gib_uuid='test-uuid'
        )
        
        # 9 gün önce gönderilmiş
        invoice.gib_sent_at = timezone.now() - timedelta(days=9)
        invoice.save()
        
        from finance.services import EFaturaService
        service = EFaturaService(tenant)
        
        can_cancel = service.can_cancel_invoice(invoice)
        assert can_cancel is False, "8 gün sonra iptal edilememeli"
