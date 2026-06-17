import requests
from django.conf import settings
from decouple import config

class EFaturaService:
    """E-Fatura entegratör servisi (Paraşüt, EDM vb.)"""
    
    def __init__(self, tenant):
        self.tenant = tenant
        self.api_url = config('EFATURA_API_URL')
        self.api_key = config('EFATURA_API_KEY')
        self.api_secret = config('EFATURA_API_SECRET')
        
        self.provider_username = tenant.efatura_username
        self.provider_password = tenant.efatura_password
    
    def send_invoice(self, invoice):
        """Faturayı GİB'e gönder"""
        payload = self._prepare_invoice_payload(invoice)
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f'{self.api_url}/invoices',
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            raise Exception('GİB bağlantısı zaman aşımına uğradı')
        except requests.exceptions.RequestException as e:
            raise Exception(f'GİB iletişim hatası: {str(e)}')
    
    def can_cancel_invoice(self, invoice):
        """
        Fatura iptal edilebilir mi? (8 günlük mevzuat kuralı)
        GİB'e göre fatura kesim tarihinden itibaren 8 gün içinde iptal edilebilir.
        Sonrasında iade faturası kesilmeli.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        if not invoice.gib_sent_at:
            return False
        
        days_passed = (timezone.now() - invoice.gib_sent_at).days
        return days_passed <= 8
    
    def cancel_invoice(self, invoice):
        """
        Faturayı iptal et (8 gün içindeyse)
        GİB'e iptal bildirimi gönder
        """
        if not self.can_cancel_invoice(invoice):
            raise Exception('Fatura 8 günlük iptal süresini geçmiş. İade faturası kesilmeli.')
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f'{self.api_url}/invoices/{invoice.gib_uuid}/cancel',
                json={'reason': 'İptal'},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            # Cari kaydı tersine çevir
            from .models import CariAccount
            CariAccount.objects.create(
                tenant=invoice.tenant,
                dealer=invoice.dealer,
                transaction_type='ADJUSTMENT',
                amount=-invoice.total_amount,
                description=f'Fatura İptali: {invoice.invoice_number}',
                invoice=invoice
            )
            
            invoice.status = 'CANCELLED'
            invoice.save()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise Exception(f'Fatura iptal edilemedi: {str(e)}')
    
    def create_return_invoice(self, original_invoice):
        """
        İade faturası oluştur (8 gün sonrası için)
        Negatif tutarlı yeni fatura
        """
        from .models import Invoice
        from datetime import date, timedelta
        
        return_invoice = Invoice.objects.create(
            tenant=original_invoice.tenant,
            dealer=original_invoice.dealer,
            order=original_invoice.order,
            invoice_number=f"{original_invoice.invoice_number}-IADE",
            due_date=date.today() + timedelta(days=30),
            subtotal=-original_invoice.subtotal,
            vat_amount=-original_invoice.vat_amount,
            total_amount=-original_invoice.total_amount,
            status='PENDING'
        )
        
        return return_invoice
    
    def _prepare_invoice_payload(self, invoice):
        """Fatura verisini API formatına çevir"""
        items = []
        for item in invoice.order.items.all():
            items.append({
                'product_code': item.product.code,
                'product_name': item.product.name,
                'quantity': float(item.quantity),
                'unit_price': float(item.unit_price),
                'vat_rate': float(item.vat_rate),
                'line_total': float(item.line_total)
            })
        
        return {
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date.isoformat(),
            'due_date': invoice.due_date.isoformat(),
            'customer': {
                'name': invoice.dealer.name,
                'tax_office': invoice.dealer.tax_office,
                'tax_number': invoice.dealer.tax_number,
                'address': invoice.dealer.address,
            },
            'items': items,
            'subtotal': float(invoice.subtotal),
            'vat_amount': float(invoice.vat_amount),
            'total_amount': float(invoice.total_amount)
        }
