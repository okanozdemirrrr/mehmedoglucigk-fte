# Production Checklist

Canlıya çıkmadan önce kontrol edilmesi gerekenler:

## ✅ Güvenlik

- [ ] `DEBUG=False` ayarlandı
- [ ] `SECRET_KEY` güçlü ve benzersiz
- [ ] `ALLOWED_HOSTS` doğru domain'leri içeriyor
- [ ] HTTPS/SSL sertifikası aktif
- [ ] Firewall kuralları ayarlandı (sadece 80, 443, 22)
- [ ] PostgreSQL sadece localhost'tan erişilebilir
- [ ] Redis şifre korumalı
- [ ] `.env` dosyası `.gitignore`'da

## ✅ Testler

- [ ] Tüm testler geçiyor: `pytest`
- [ ] Coverage %80'in üzerinde: `pytest --cov`
- [ ] Concurrency testleri geçiyor
- [ ] Tenant isolation testleri geçiyor
- [ ] E-Fatura integration testleri geçiyor

## ✅ Veritabanı

- [ ] PostgreSQL 14+ kurulu
- [ ] Veritabanı yedekleme cron job'u aktif
- [ ] Connection pooling ayarlandı
- [ ] Index'ler oluşturuldu: `python manage.py migrate`
- [ ] Superuser oluşturuldu

## ✅ Monitoring

- [ ] Sentry DSN ayarlandı
- [ ] Sentry test edildi (test exception gönder)
- [ ] Log dosyaları rotasyonu ayarlandı
- [ ] Disk kullanımı monitoring
- [ ] CPU/RAM monitoring

## ✅ E-Fatura

- [ ] Entegratör API credentials ayarlandı
- [ ] Test ortamında fatura gönderimi test edildi
- [ ] 8 günlük iptal kuralı test edildi
- [ ] Timeout senaryosu test edildi
- [ ] Rollback mekanizması test edildi

## ✅ Performance

- [ ] Static dosyalar collect edildi: `python manage.py collectstatic`
- [ ] Gunicorn worker sayısı ayarlandı (CPU * 2 + 1)
- [ ] Nginx gzip compression aktif
- [ ] Redis cache aktif
- [ ] Database query optimization yapıldı (N+1 problemi yok)

## ✅ Backup

- [ ] Veritabanı günlük yedekleme
- [ ] Media dosyaları yedekleme
- [ ] Yedekleme restore testi yapıldı
- [ ] Off-site backup (farklı sunucu/bölge)

## ✅ Celery

- [ ] Celery worker çalışıyor
- [ ] Celery beat (scheduled tasks) çalışıyor
- [ ] Supervisor ile otomatik restart
- [ ] Dead letter queue ayarlandı

## ✅ Frontend

- [ ] Production build: `npm run build`
- [ ] API endpoints doğru
- [ ] Mobile responsive test edildi
- [ ] Cross-browser test (Chrome, Safari, Firefox)
- [ ] Slow network test edildi

## ✅ Dokümantasyon

- [ ] API dokümantasyonu güncel
- [ ] Deployment guide güncel
- [ ] README güncel
- [ ] Acil durum prosedürleri yazıldı

## ✅ İlk Müşteri Hazırlığı

- [ ] Demo tenant oluşturuldu
- [ ] Demo ürünler eklendi
- [ ] Demo bayi oluşturuldu
- [ ] Sipariş akışı end-to-end test edildi
- [ ] E-Fatura test ortamında kesildi
- [ ] Admin paneli eğitim videosu hazırlandı
- [ ] Bayi mobil arayüz eğitim videosu hazırlandı

## ✅ Acil Durum Planı

- [ ] Rollback prosedürü hazır
- [ ] Veritabanı restore prosedürü test edildi
- [ ] 7/24 on-call kişi belirlendi
- [ ] Sentry alert'leri Slack/Email'e bağlandı
- [ ] Downtime durumunda müşteri bilgilendirme planı

## 🚨 Kritik Kontroller

### Concurrency Test
```bash
pytest tests/test_concurrency.py -v
```
**Sonuç**: PASS olmalı

### Tenant Isolation Test
```bash
pytest tests/test_tenant_isolation.py -v
```
**Sonuç**: PASS olmalı

### E-Fatura Test
```bash
pytest tests/test_efatura_integration.py -v
```
**Sonuç**: PASS olmalı

### Sentry Test
```python
# Django shell
from sentry_sdk import capture_message
capture_message("Production test", level="info")
```
**Sonuç**: Sentry dashboard'da görünmeli

### Load Test (Opsiyonel ama önerilen)
```bash
locust -f tests/load_test.py --headless -u 50 -r 10 -t 5m
```
**Hedef**: 
- Response time < 500ms
- Error rate < 1%

---

## ✅ Tamamlandı mı?

Yukarıdaki tüm checkbox'lar işaretlendiyse:

**🎉 Production'a hazırsınız!**

Aksi halde:
**⚠️ EKSİK OLAN MADDELERI TAMAMLAYIN!**

---

**Son Kontrol**: 
```bash
python manage.py check --deploy
```

Bu komut Django'nun production hazırlık kontrollerini yapar.
