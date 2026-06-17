#!/bin/bash

echo "=== Mergen SaaS Kurulum Scripti ==="

# Virtual environment oluştur
echo "1. Virtual environment oluşturuluyor..."
python -m venv venv

# Virtual environment aktif et
echo "2. Virtual environment aktif ediliyor..."
source venv/bin/activate

# Gereksinimleri yükle
echo "3. Python paketleri yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt

# .env dosyası oluştur
if [ ! -f .env ]; then
    echo "4. .env dosyası oluşturuluyor..."
    cp .env.example .env
    echo "UYARI: .env dosyasını düzenleyip veritabanı bilgilerini girin!"
else
    echo "4. .env dosyası zaten mevcut."
fi

# Migrasyonları oluştur
echo "5. Veritabanı migrasyonları oluşturuluyor..."
python manage.py makemigrations

# Migrasyonları uygula
echo "6. Migrasyonlar uygulanıyor..."
python manage.py migrate

echo ""
echo "=== Kurulum Tamamlandı! ==="
echo ""
echo "Sonraki adımlar:"
echo "1. .env dosyasını düzenleyin"
echo "2. Superuser oluşturun: python manage.py createsuperuser"
echo "3. Sunucuyu başlatın: python manage.py runserver"
echo ""
