import pytest
from django.contrib.auth import get_user_model
from core.models import Tenant
from accounts.models import Dealer
from products.models import Product, Category

User = get_user_model()

@pytest.fixture
def tenant(db):
    """Test tenant oluştur"""
    return Tenant.objects.create(
        name="Test Firma",
        slug="test-firma",
        tax_office="Test VD",
        tax_number="1234567890",
        address="Test Adres",
        phone="5551234567",
        email="test@test.com"
    )

@pytest.fixture
def admin_user(db, tenant):
    """Admin kullanıcı"""
    return User.objects.create_user(
        email="admin@test.com",
        password="testpass123",
        role="ADMIN",
        tenant=tenant,
        is_staff=True
    )

@pytest.fixture
def dealer(db, tenant):
    """Test bayisi"""
    return Dealer.objects.create(
        tenant=tenant,
        code="BAY001",
        name="Test Bayi",
        tax_office="Test VD",
        tax_number="9876543210",
        address="Bayi Adres",
        city="İstanbul",
        district="Kadıköy",
        phone="5559876543",
        credit_limit=10000,
        payment_term_days=30,
        discount_rate=5
    )

@pytest.fixture
def dealer_user(db, dealer):
    """Bayi kullanıcısı"""
    user = User.objects.create_user(
        email="dealer@test.com",
        password="testpass123",
        role="DEALER",
        tenant=dealer.tenant
    )
    user.dealer = dealer
    user.save()
    return user

@pytest.fixture
def category(db, tenant):
    """Test kategorisi"""
    return Category.objects.create(
        tenant=tenant,
        code="KAT001",
        name="Çiğköfte"
    )

@pytest.fixture
def product(db, tenant, category):
    """Test ürünü"""
    return Product.objects.create(
        tenant=tenant,
        category=category,
        code="URN001",
        name="Çiğköfte 1kg",
        unit="KG",
        base_price=45.00,
        vat_rate=20.00,
        stock_quantity=100
    )
