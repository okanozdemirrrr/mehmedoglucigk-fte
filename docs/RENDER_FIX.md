# Render deploy notları

## Mevcut servis (tek tık düzeltme)

Render Dashboard → **mehmedoglucigk-fte** → **Settings**:

1. **Language** → **Docker** yap → Save
2. **Environment** → `DATABASE_URL` = Neon pooled connection string
3. **Manual Deploy** → Deploy latest commit

Dockerfile repo kökünde — start command, Python sürümü, migrate hepsi otomatik.

## Sıfırdan (Blueprint)

1. Render → **New +** → **Blueprint**
2. Repo: `okanozdemirrrr/mehmedoglucigk-fte`
3. `DATABASE_URL` gir → Apply

## Test

https://mehmedoglucigk-fte.onrender.com/api/health/
