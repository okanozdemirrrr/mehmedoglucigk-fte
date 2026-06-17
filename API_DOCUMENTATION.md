# Mergen SaaS - API Dokümantasyonu

## Kimlik Doğrulama

Tüm API istekleri kimlik doğrulama gerektirir. Session authentication kullanılmaktadır.

## Temel URL
```
http://localhost:8000/api/
```

## Endpoints

### 1. Ürünler (Products)

#### Ürün Listesi
```
GET /api/products/products/
```

Query Parameters:
- `category`: Kategori ID'sine göre filtrele
- `is_active`: Aktif/pasif filtresi (true/false)
- `search`: Ürün kodu, adı veya barkod ile arama

Response:
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "code": "URN001",
      "name": "Çiğköfte 1kg",
      "category": 1,
      "category_name": "Çiğköfte",
      "base_price": "45.00",
      "vat_rate": "20.00",
      "stock_quantity": "150.000",
      "is_active": true
    }
  ]
}
```

#### Ürün Detay
```
GET /api/products/products/{id}/
```

#### Yeni Ürün (Admin)
```
POST /api/products/products/
```

Body:
```json
{
  "code": "URN001",
  "name": "Çiğköfte 1kg",
  "category": 1,
  "unit": "KG",
  "base_price": "45.00",
  "vat_rate": "20.00",
  "min_stock_level": "50.000"
}
```

### 2. Siparişler (Orders)

#### Sipariş Listesi
```
GET /api/orders/orders/
```

Query Parameters:
- `status`: Sipariş durumu (DRAFT, PENDING, APPROVED, vb.)
- `dealer`: Bayi ID'sine göre filtrele

#### Yeni Sipariş
```
POST /api/orders/orders/
```

Body:
```json
{
  "dealer": 1,
  "notes": "Acil teslimat",
  "items": [
    {
      "product": 1,
      "quantity": "10.000"
    },
    {
      "product": 2,
      "quantity": "5.000"
    }
  ]
}
```

Response:
```json
{
  "id": 1,
  "order_number": "ORD-FIRMA-000001",
  "dealer": 1,
  "dealer_name": "Bayi A",
  "status": "PENDING",
  "subtotal": "450.00",
  "discount_amount": "22.50",
  "vat_amount": "90.00",
  "total_amount": "517.50",
  "items": [...]
}
```

#### Sipariş Onaylama (Admin)
```
POST /api/orders/orders/{id}/approve/
```

Response:
```json
{
  "status": "Sipariş onaylandı"
}
```

#### Sipariş İptal (Admin)
```
POST /api/orders/orders/{id}/cancel/
```

### 3. Faturalar (Invoices)

#### Fatura Listesi (Admin)
```
GET /api/finance/invoices/
```

#### Fatura Detay
```
GET /api/finance/invoices/{id}/
```

#### Faturayı GİB'e Gönder (Admin)
```
POST /api/finance/invoices/{id}/send_to_gib/
```

Response:
```json
{
  "status": "Fatura GİB'e gönderildi",
  "gib_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 4. Cari Hesap

#### Cari Hareketler
```
GET /api/finance/cari/
```

Query Parameters:
- `dealer`: Bayi ID
- `transaction_type`: İşlem tipi (INVOICE, PAYMENT, RETURN, ADJUSTMENT)

#### Bayi Bakiyesi
```
GET /api/finance/cari/balance/?dealer={dealer_id}
```

Response:
```json
{
  "dealer_id": 1,
  "balance": "5250.00"
}
```

## Hata Kodları

- `400 Bad Request`: Geçersiz istek
- `401 Unauthorized`: Kimlik doğrulama gerekli
- `403 Forbidden`: Yetki yok
- `404 Not Found`: Kayıt bulunamadı
- `500 Internal Server Error`: Sunucu hatası

## Güvenlik

### Tenant İzolasyonu
- Her kullanıcı sadece kendi tenant'ına ait verileri görebilir
- Bayiler sadece kendi siparişlerini ve cari hareketlerini görebilir
- Admin kullanıcılar tenant içindeki tüm verilere erişebilir

### Roller
- `SUPERADMIN`: Tüm sistemlere erişim
- `ADMIN`: Tenant içinde tam yetki
- `DEALER`: Sadece kendi verileri
- `STAFF`: Sınırlı admin yetkisi
