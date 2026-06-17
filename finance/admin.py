from django.contrib import admin
from .models import CariAccount, Invoice

@admin.register(CariAccount)
class CariAccountAdmin(admin.ModelAdmin):
    list_display = ['dealer', 'transaction_type', 'amount', 'transaction_date']
    list_filter = ['transaction_type', 'tenant', 'transaction_date']
    search_fields = ['dealer__code', 'dealer__name', 'description']
    readonly_fields = ['transaction_date', 'created_at']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'dealer', 'status', 'total_amount', 'invoice_date']
    list_filter = ['status', 'tenant', 'invoice_date']
    search_fields = ['invoice_number', 'dealer__name', 'gib_uuid']
    readonly_fields = ['invoice_date', 'gib_sent_at', 'gib_response', 'created_at']
    
    actions = ['send_to_gib_action']
    
    def send_to_gib_action(self, request, queryset):
        success = 0
        for invoice in queryset:
            try:
                invoice.send_to_gib()
                success += 1
            except Exception as e:
                self.message_user(request, f'{invoice.invoice_number}: {str(e)}', level='error')
        
        if success:
            self.message_user(request, f'{success} fatura başarıyla GİB\'e gönderildi')
    
    send_to_gib_action.short_description = 'Seçili faturaları GİB\'e gönder'
