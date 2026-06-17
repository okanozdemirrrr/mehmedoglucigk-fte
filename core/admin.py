from django.contrib import admin
from .models import Tenant

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'tax_number', 'is_active', 'subscription_start', 'subscription_end']
    list_filter = ['is_active', 'subscription_start']
    search_fields = ['name', 'tax_number', 'email']
    prepopulated_fields = {'slug': ('name',)}
