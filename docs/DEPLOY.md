# Canlıya Alma — Render (Backend) + Vercel (Frontend)

## Özet

| Parça | Adres |
|-------|-------|
| Frontend | https://frontend-black-psi-97.vercel.app |
| Backend (Render) | https://mehmedoglu-b2b-api.onrender.com |

---

## ADIM 1 — GitHub'a kod yükle (5 dk)

1. https://github.com → **New repository** → isim: `mehmedoglu-b2b`
2. Bilgisayarda PowerShell:

```powershell
cd c:\Users\90505\Desktop\mehmedoğlu_çiğköfte
git init
git add .
git commit -m "Production deploy hazırlığı"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADINIZ/mehmedoglu-b2b.git
git push -u origin main
```

---

## ADIM 2 — Render'da backend aç (5 dk)

1. https://render.com → ücretsiz kayıt
2. **New +** → **Blueprint**
3. GitHub repo'yu bağla → `render.yaml` otomatik algılanır → **Apply**
4. **DATABASE_URL** sorulunca Neon bağlantı dizesini yapıştır:
   - Neon Console → Connection string → **Pooled connection**
   - Örnek: `postgresql://neondb_owner:...@ep-....neon.tech/neondb?sslmode=require`
5. Deploy bitince test et:
   - https://mehmedoglu-b2b-api.onrender.com/api/health/
   - `{"status":"ok"}` görmelisin

> Ücretsiz plan: 15 dk kullanılmazsa uyur. İlk istek 30-60 sn sürebilir.

---

## ADIM 3 — Vercel'e API adresini bağla

Vercel Dashboard → `frontend` projesi → **Settings** → **Environment Variables**:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://mehmedoglu-b2b-api.onrender.com/api/` |

**Production** için kaydet → **Deployments** → son deploy → **Redeploy**

Veya terminalden:

```powershell
cd frontend
echo https://mehmedoglu-b2b-api.onrender.com/api/ | vercel env add VITE_API_URL production
vercel --prod --yes
```

---

## ADIM 4 — Test

1. https://frontend-black-psi-97.vercel.app/login
2. `admin@mergen.com` / `123456`
3. Giriş başarılı olmalı

---

## Sorun giderme

| Hata | Çözüm |
|------|-------|
| Backend çalışıyor mu? | Render deploy bitti mi? health URL'yi aç |
| CORS hatası | Render'da `CORS_ORIGINS` içinde Vercel URL var mı |
| 502 / timeout | Render uyumuş — sayfayı yenile, 1 dk bekle |
| DB hatası | `DATABASE_URL` Neon pooled string mi |
