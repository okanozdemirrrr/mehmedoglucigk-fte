# Test Dokümantasyonu

## Test Çalıştırma

### Tüm Testler
```bash
pytest
```

### Coverage Raporu
```bash
pytest --cov --cov-report=html
# Rapor: htmlcov/index.html
```

### Belirli Test Dosyası
```bash
pytest tests/test_concurrency.py -v
```

### Belirli Test
```bash
pytest tests/test_concurrency.py::TestStockConcurrency::test_concurrent_stock_deduction -v
```

## Test Kategorileri

### 1. Concurrency Tests (Kritik!)
**Dosya**: `tests/test_concurrency.py`

**Senaryo**: İki bayi aynı anda son stoku sipariş eder
```bash
pytest tests/test_concurrency.py -v
```

**Beklenen**: Sadece bir sipariş başarılı olmalı, diğeri "Yetersiz stok" hatası almalı.

### 2. Tenant Isolation Tests
**Dosya**: `tests/test_tenant_isolation.py`

**Senaryo**: Bir bayi başka tenant'ın verisini görebilir mi?
```bash
pytest tests/test_tenant_isolation.py -v
```

**Beklenen**: Her tenant sadece kendi verisini görmeli.

### 3. E-Fatura Integration Tests
**Dosya**: `tests/test_efatura_integration.py`

**Senaryolar**:
- ✅ Başarılı fatura gönderimi
- ✅ GİB timeout durumu
- ✅ 8 gün içinde iptal
- ✅ 8 gün sonrası iade faturası

```bash
pytest tests/test_efatura_integration.py -v
```

## Test Coverage Hedefi

**Minimum**: %80
**Hedef**: %90+

### Kritik Modüller (Coverage %100 olmalı)
- `orders.models.Order.approve()` - Stok düşümü
- `finance.models.Invoice.send_to_gib()` - E-Fatura
- `core.middleware.TenantMiddleware` - Güvenlik
- `core.permissions.*` - Yetkilendirme

## Mock Kullanımı

### E-Fatura API Mock
```python
from unittest.mock import patch, Mock

@patch('finance.services.requests.post')
def test_invoice(mock_post):
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: {'uuid': 'test-uuid'}
    )
    # Test kodu...
```

## Continuous Integration

GitHub Actions ile otomatik test:
- Her push'ta testler çalışır
- Coverage %80'in altına düşerse CI fail olur
- Pull request merge için testlerin geçmesi zorunlu

## Load Testing (Opsiyonel)

### Locust ile yük testi
```bash
pip install locust
locust -f tests/load_test.py
```

**Senaryo**: 100 bayi aynı anda sipariş verir
**Hedef**: Response time < 500ms, Success rate > 99%

## Test Veritabanı

Testler otomatik olarak `test_` prefix'li veritabanı kullanır.
Her test sonrası otomatik temizlenir.

```python
# pytest.ini
--reuse-db  # Veritabanını yeniden kullan (hızlı)
```

## Debugging

### Tek test debug
```bash
pytest tests/test_concurrency.py::test_name -v -s --pdb
```

### Print çıktılarını göster
```bash
pytest -v -s
```

## Pre-commit Hook (Önerilen)

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest --cov --cov-fail-under=80
if [ $? -ne 0 ]; then
    echo "Testler başarısız! Commit iptal edildi."
    exit 1
fi
```

## Sonuç

**Test olmadan production'a çıkmayın!**

Özellikle:
- Concurrency testleri (stok düşümü)
- Tenant isolation testleri (güvenlik)
- E-Fatura integration testleri (para)

Bu üç kategori %100 coverage'a sahip olmalı.
