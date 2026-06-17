"""
KRİTİK: Concurrency (Eşzamanlılık) Testleri
İki bayi aynı anda son stoku sipariş ettiğinde ne olur?
"""
import pytest
from django.db import transaction
from django.test import TransactionTestCase
from concurrent.futures import ThreadPoolExecutor, as_completed
from orders.models import Order, OrderItem
from products.models import Product

@pytest.mark.django_db(transaction=True)
class TestStockConcurrency(TransactionTestCase):
    """Stok düşümü concurrency testleri"""
    
    def setUp(self):
        from tests.conftest import tenant, dealer, product, category
        self.tenant = tenant(self)
        self.category = category(self, self.tenant)
        self.product = product(self, self.tenant, self.category)
        self.dealer1 = dealer(self, self.tenant)
        self.dealer2 = dealer(self, self.tenant)
        
        # Son 10 kilo stok
        self.product.stock_quantity = 10
        self.product.save()
    
    def create_order_and_approve(self, dealer, quantity):
        """Sipariş oluştur ve onayla"""
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    tenant=self.tenant,
                    dealer=dealer,
                    order_number=f"TEST-{dealer.code}-001",
                    status='PENDING'
                )
                
                OrderItem.objects.create(
                    order=order,
                    product=self.product,
                    quantity=quantity,
                    unit_price=self.product.base_price,
                    vat_rate=self.product.vat_rate
                )
                
                # Stok kontrolü ve düşümü (ATOMIC)
                product = Product.objects.select_for_update().get(id=self.product.id)
                
                if product.stock_quantity < quantity:
                    raise ValueError(f"Yetersiz stok: {product.stock_quantity}")
                
                product.stock_quantity -= quantity
                product.save()
                
                order.status = 'APPROVED'
                order.save()
                
                return {'success': True, 'order': order.id}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_concurrent_stock_deduction(self):
        """İki bayi aynı anda 10 kilo sipariş verirse sadece biri başarılı olmalı"""
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(self.create_order_and_approve, self.dealer1, 10),
                executor.submit(self.create_order_and_approve, self.dealer2, 10)
            ]
            
            results = [future.result() for future in as_completed(futures)]
        
        # Sonuçları kontrol et
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        # Sadece bir sipariş başarılı olmalı
        assert len(successful) == 1, "İki sipariş de geçti! Race condition var!"
        assert len(failed) == 1, "İki sipariş de başarısız! Mantık hatası var!"
        
        # Stok kontrolü
        self.product.refresh_from_db()
        assert self.product.stock_quantity == 0, f"Stok {self.product.stock_quantity} olmamalı!"
        
        # Hata mesajı kontrolü
        assert "Yetersiz stok" in failed[0]['error']
