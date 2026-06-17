from rest_framework import serializers
from .models import Invoice, CariAccount

class InvoiceSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(source='dealer.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'dealer', 'dealer_name', 'order', 'order_number',
            'invoice_date', 'due_date', 'status', 'status_display',
            'subtotal', 'vat_amount', 'total_amount', 'gib_uuid', 'gib_sent_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'invoice_date', 'gib_uuid', 
            'gib_sent_at', 'status'
        ]

class CariAccountSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(source='dealer.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = CariAccount
        fields = [
            'id', 'dealer', 'dealer_name', 'transaction_date', 
            'transaction_type', 'transaction_type_display', 
            'amount', 'description'
        ]
        read_only_fields = ['id', 'transaction_date']
