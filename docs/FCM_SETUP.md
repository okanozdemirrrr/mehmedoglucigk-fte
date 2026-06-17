# Firebase Push — Web + Android Kurulumu

Aynı Django backend hem tarayıcı (Web Push) hem Android (native FCM) token'larına bildirim gönderir.

---

## 1. Firebase Console — Web App

1. **Project settings** → **General** → **Web (`</>`)** ekle
2. Config değerlerini `frontend/.env` dosyasına yaz

## 2. Firebase Console — Android App (ZORUNLU)

1. **Project settings** → **General** → **Android** ikonu
2. **Android package name:** `com.mergen.b2b` (Capacitor ile aynı — değiştirmeyin)
3. App nickname: `Mergen B2B Android` → **Register app**
4. İndirilen **`google-services.json`** dosyasını şuraya koy:

```
frontend/android/app/google-services.json
```

> Bu dosya olmadan Android push **çalışmaz**. Gradle build sırasında otomatik algılanır.

## 3. VAPID Key (sadece Web tarayıcı için)

1. **Project settings** → **Cloud Messaging**
2. **Web Push certificates** → **Generate key pair**
3. `frontend/.env` → `VITE_FIREBASE_VAPID_KEY=...`

## 4. Service Account JSON (Django backend için)

1. **Project settings** → **Service accounts** → **Generate new private key**
2. Proje kökü `.env`:

```
FIREBASE_CREDENTIALS_PATH=C:\path\to\mehmedoglucigkofte-adminsdk.json
```

## 5. Ortam Değişkenleri

### `frontend/.env`

```env
# Telefon/emülatör Django'ya erişsin (ipconfig ile LAN IP'nizi bulun)
VITE_API_URL=http://192.168.1.100:8000/api/

VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=mehmedoglucigkofte.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=mehmedoglucigkofte
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=480419731243
VITE_FIREBASE_APP_ID=...
VITE_FIREBASE_VAPID_KEY=...
```

### Proje kökü `.env` (Django)

```env
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100
CORS_ORIGINS=http://localhost:3000,https://localhost
FIREBASE_CREDENTIALS_PATH=C:\path\to\adminsdk.json
```

| Ortam | VITE_API_URL |
|-------|----------------|
| Tarayıcı (dev) | `http://localhost:8000/api/` |
| Android emülatör | `http://10.0.2.2:8000/api/` |
| Android fiziksel cihaz | `http://BILGISAYAR_IP:8000/api/` |

---

## 6. Android APK Derleme

```powershell
cd frontend
copy .env.example .env
# .env doldur + google-services.json koy

npm run cap:sync
npm run cap:open:android
```

Android Studio:
1. Telefonu USB ile bağla veya emülatör aç
2. **Run** (▶) — uygulama yüklenir
3. Giriş yap → bildirim izni ver → token DB'ye kaydolur

Release APK:
- **Build → Generate Signed Bundle / APK**

---

## 7. Test Senaryosu

1. **Admin telefonda** giriş yap (bildirim izni ver)
2. **Bayi** (web veya başka cihaz) sipariş oluştur
3. Admin telefonuna: **"Yeni Sipariş Geldi!"**
4. Admin onayla → Bayi telefonuna: **"Siparişiniz Yola Çıktı"**
5. Bayi teslim al → Admin telefonuna: **"Teslimat Onaylandı"**

Token kontrolü: Neon `users` tablosu → `fcm_token` dolu mu?

---

## Bildirim Tetikleyicileri

| Olay | Alıcı | Başlık |
|------|-------|--------|
| Yeni sipariş (PENDING) | Admin/Dağıtıcı | Yeni Sipariş Geldi! |
| PREPARING / ON_THE_WAY | Bayi | Siparişiniz Yola Çıktı |
| DELIVERED | Admin/Dağıtıcı | Teslimat Onaylandı |

API: `POST /api/accounts/fcm-token/` → `{ "fcm_token": "..." }`
