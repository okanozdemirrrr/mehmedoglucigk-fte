from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['line_total', 'vat_amount']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'dealer', 'status', 'total_amount', 'order_date']
    list_filter = ['status', 'tenant', 'order_date']
    search_fields = ['order_number', 'dealer__name', 'dealer__code']
    readonly_fields = ['order_date', 'approved_at', 'approved_by', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(tenant=request.user.tenant)
        return qs
