# Mergen SaaS - Frontend

Mobile-first React uygulaması (Vite + TailwindCSS)

## Kurulum

```bash
cd frontend
npm install
npm run dev
```

## Özellikler

### Bayi Arayüzü
- ✅ Mobil öncelikli sipariş ekranı
- ✅ Ürün listesi ve arama
- ✅ Sepet yönetimi
- ✅ Cari bakiye görüntüleme
- ✅ Sipariş geçmişi

### Admin Arayüzü
- ✅ Bekleyen siparişler
- ✅ Tek tıkla onay/iptal
- ✅ Stok yönetimi
- ✅ Fatura oluşturma
- ✅ Raporlar

## Teknolojiler

- **React 18**: UI framework
- **Vite**: Build tool
- **TailwindCSS**: Styling
- **React Query**: API state management
- **Axios**: HTTP client
- **Zustand**: Global state
- **React Hook Form**: Form yönetimi
- **Sonner**: Toast notifications

## API Entegrasyonu

Backend ile `/api` proxy üzerinden iletişim kurar.

```javascript
// Örnek kullanım
import { ordersApi } from './api/orders';

const { data } = useQuery({
  queryKey: ['orders'],
  queryFn: () => ordersApi.getOrders()
});
```

## Production Build

```bash
npm run build
```

Build dosyaları `dist/` klasörüne oluşturulur ve Django'nun `staticfiles` dizinine kopyalanabilir.
