from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Dealer

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'role', 'tenant', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'tenant']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Yetkilendirme', {'fields': ('role', 'tenant', 'dealer', 'is_active', 'is_staff', 'is_superuser')}),
        ('Tarihler', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'tenant'),
        }),
    )

@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'tenant', 'city', 'is_active', 'credit_limit']
    list_filter = ['is_active', 'tenant', 'city']
    search_fields = ['code', 'name', 'tax_number', 'phone']
    readonly_fields = ['created_at', 'updated_at']
