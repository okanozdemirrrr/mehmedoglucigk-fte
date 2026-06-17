@echo off
echo === Mergen SaaS Kurulum Scripti ===

REM Virtual environment olustur
echo 1. Virtual environment olusturuluyor...
python -m venv venv

REM Virtual environment aktif et
echo 2. Virtual environment aktif ediliyor...
call venv\Scripts\activate.bat

REM Gereksinimleri yukle
echo 3. Python paketleri yukleniyor...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM .env dosyasi olustur
if not exist .env (
    echo 4. .env dosyasi olusturuluyor...
    copy .env.example .env
    echo UYARI: .env dosyasini duzenleyip veritabani bilgilerini girin!
) else (
    echo 4. .env dosyasi zaten mevcut.
)

REM Migrasyonlari olustur
echo 5. Veritabani migrasyonlari olusturuluyor...
python manage.py makemigrations

REM Migrasyonlari uygula
echo 6. Migrasyonlar uygulanıyor...
python manage.py migrate

echo.
echo === Kurulum Tamamlandi! ===
echo.
echo Sonraki adimlar:
echo 1. .env dosyasini duzenleyin
echo 2. Superuser olusturun: python manage.py createsuperuser
echo 3. Sunucuyu baslatin: python manage.py runserver
echo.
pause
