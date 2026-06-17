# Mergen SaaS - Deployment Rehberi

## Production Ortamı Hazırlığı

### 1. Sunucu Gereksinimleri

**Minimum:**
- CPU: 2 Core
- RAM: 4 GB
- Disk: 50 GB SSD
- OS: Ubuntu 22.04 LTS

**Önerilen:**
- CPU: 4 Core
- RAM: 8 GB
- Disk: 100 GB SSD

### 2. Gerekli Servisler

```bash
# PostgreSQL 14+
sudo apt update
sudo apt install postgresql postgresql-contrib

# Redis
sudo apt install redis-server

# Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Nginx
sudo apt install nginx

# Supervisor (Celery için)
sudo apt install supervisor
```

### 3. Veritabanı Kurulumu

```bash
sudo -u postgres psql

CREATE DATABASE mergen_saas;
CREATE USER mergen_user WITH PASSWORD 'güçlü_şifre_buraya';
ALTER ROLE mergen_user SET client_encoding TO 'utf8';
ALTER ROLE mergen_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE mergen_user SET timezone TO 'Europe/Istanbul';
GRANT ALL PRIVILEGES ON DATABASE mergen_saas TO mergen_user;
\q
```

### 4. Uygulama Kurulumu

```bash
# Proje dizini oluştur
sudo mkdir -p /var/www/mergen_saas
sudo chown $USER:$USER /var/www/mergen_saas
cd /var/www/mergen_saas

# Kodu çek (Git kullanarak)
git clone <repository_url> .

# Virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Paketleri yükle
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 5. Ortam Değişkenleri (.env)

```bash
nano .env
```

```env
SECRET_KEY=production-secret-key-buraya-50-karakter
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_NAME=mergen_saas
DB_USER=mergen_user
DB_PASSWORD=güçlü_şifre_buraya
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=https://yourdomain.com

EFATURA_API_URL=https://api.efatura-provider.com
EFATURA_API_KEY=your-api-key
EFATURA_API_SECRET=your-api-secret
```

### 6. Django Hazırlık

```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

### 7. Gunicorn Konfigürasyonu

```bash
sudo nano /etc/systemd/system/mergen_saas.service
```

```ini
[Unit]
Description=Mergen SaaS Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/mergen_saas
Environment="PATH=/var/www/mergen_saas/venv/bin"
ExecStart=/var/www/mergen_saas/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/mergen_saas/mergen_saas.sock \
    --timeout 120 \
    mergen_saas.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start mergen_saas
sudo systemctl enable mergen_saas
```

### 8. Celery Konfigürasyonu

```bash
sudo nano /etc/supervisor/conf.d/mergen_celery.conf
```

```ini
[program:mergen_celery]
command=/var/www/mergen_saas/venv/bin/celery -A mergen_saas worker -l info
directory=/var/www/mergen_saas
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/mergen_celery.log
```

```bash
sudo mkdir -p /var/log/celery
sudo chown www-data:www-data /var/log/celery
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mergen_celery
```

### 9. Nginx Konfigürasyonu

```bash
sudo nano /etc/nginx/sites-available/mergen_saas
```

```nginx
upstream mergen_app {
    server unix:/var/www/mergen_saas/mergen_saas.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    client_max_body_size 20M;
    
    location /static/ {
        alias /var/www/mergen_saas/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /var/www/mergen_saas/media/;
        expires 30d;
    }
    
    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://mergen_app;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/mergen_saas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. SSL Sertifikası (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 11. Güvenlik

```bash
# Firewall
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable

# PostgreSQL sadece localhost
sudo nano /etc/postgresql/14/main/pg_hba.conf
# local   all   all   peer
# host    all   all   127.0.0.1/32   md5

sudo systemctl restart postgresql
```

### 12. Yedekleme

```bash
# Veritabanı yedeği (crontab)
0 2 * * * pg_dump -U mergen_user mergen_saas > /backups/db_$(date +\%Y\%m\%d).sql

# Media dosyaları
0 3 * * * rsync -av /var/www/mergen_saas/media/ /backups/media/
```

### 13. Monitoring

```bash
# Log dosyaları
tail -f /var/log/nginx/error.log
tail -f /var/log/celery/mergen_celery.log
sudo journalctl -u mergen_saas -f
```

## Güncelleme Prosedürü

```bash
cd /var/www/mergen_saas
source venv/bin/activate

# Kodu güncelle
git pull origin main

# Paketleri güncelle
pip install -r requirements.txt

# Migrasyonlar
python manage.py migrate

# Static dosyalar
python manage.py collectstatic --noinput

# Servisleri yeniden başlat
sudo systemctl restart mergen_saas
sudo supervisorctl restart mergen_celery
```

## Performans Optimizasyonu

### PostgreSQL Tuning
```sql
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET work_mem = '32MB';
SELECT pg_reload_conf();
```

### Redis Tuning
```bash
sudo nano /etc/redis/redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru
```

## Sorun Giderme

### Gunicorn çalışmıyor
```bash
sudo systemctl status mergen_saas
sudo journalctl -u mergen_saas -n 50
```

### Celery çalışmıyor
```bash
sudo supervisorctl status mergen_celery
tail -f /var/log/celery/mergen_celery.log
```

### 502 Bad Gateway
```bash
# Socket dosyasını kontrol et
ls -la /var/www/mergen_saas/mergen_saas.sock

# Nginx loglarını kontrol et
tail -f /var/log/nginx/error.log
```
