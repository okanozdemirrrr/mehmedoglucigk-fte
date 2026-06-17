"""
Tenant İzolasyon Testleri
Bir bayi başka tenant'ın verisini görebilir mi?
"""
import pytest
from django.test import RequestFactory
from rest_framework.test import force_authenticate
from products.views import ProductViewSet
from orders.views import OrderViewSet

@pytest.mark.django_db
class TestTenantIsolation:
    
    def test_dealer_cannot_see_other_tenant_products(self, tenant, dealer_user, product):
        """Bayi başka tenant'ın ürünlerini görememeli"""
        from core.models import Tenant
        from products.models import Product, Category
        
        # İkinci tenant ve ürün
        tenant2 = Tenant.objects.create(
            name="Rakip Firma", slug="rakip", tax_office="Test VD",
            tax_number="9999999999", address="Adres", phone="555", email="rakip@test.com"
        )
        
        category2 = Category.objects.create(tenant=tenant2, code="KAT2", name="Kategori 2")
        product2 = Product.objects.create(
            tenant=tenant2, category=category2, code="URN002",
            name="Rakip Ürün", base_price=50, vat_rate=20, stock_quantity=100
        )
        
        # Request oluştur
        factory = RequestFactory()
        request = factory.get('/api/products/products/')
        request.tenant = tenant
        force_authenticate(request, user=dealer_user)
        
        # ViewSet çağır
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        
        # Sadece kendi tenant'ının ürünlerini görmeli
        assert response.status_code == 200
        product_ids = [p['id'] for p in response.data['results']]
        
        assert product.id in product_ids, "Kendi ürününü görememeli değil!"
        assert product2.id not in product_ids, "Başka tenant'ın ürününü görmemeli!"
    
    def test_dealer_cannot_access_other_dealer_orders(self, tenant, dealer, dealer_user):
        """Bir bayi başka bayinin siparişlerini görememeli"""
        from accounts.models import Dealer, User
        from orders.models import Order
        
        # İkinci bayi
        dealer2 = Dealer.objects.create(
            tenant=tenant, code="BAY002", name="Bayi 2",
            tax_office="VD", tax_number="1111111111",
            address="Adres", city="İstanbul", district="Beşiktaş",
            phone="555", credit_limit=5000
        )
        
        # Siparişler
        order1 = Order.objects.create(
            tenant=tenant, dealer=dealer, order_number="ORD-001",
            status='PENDING', total_amount=100
        )
        
        order2 = Order.objects.create(
            tenant=tenant, dealer=dealer2, order_number="ORD-002",
            status='PENDING', total_amount=200
        )
        
        # Request
        factory = RequestFactory()
        request = factory.get('/api/orders/orders/')
        request.tenant = tenant
        force_authenticate(request, user=dealer_user)
        
        view = OrderViewSet.as_view({'get': 'list'})
        response = view(request)
        
        assert response.status_code == 200
        order_ids = [o['id'] for o in response.data['results']]
        
        assert order1.id in order_ids, "Kendi siparişini görmeli"
        assert order2.id not in order_ids, "Başka bayinin siparişini görmemeli!"
