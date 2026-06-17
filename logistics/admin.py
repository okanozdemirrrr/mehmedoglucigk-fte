from django.contrib import admin
from .models import Vehicle, Route, Shipment

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'brand', 'model', 'capacity', 'is_active']
    list_filter = ['is_active', 'tenant']
    search_fields = ['plate_number', 'brand', 'model']

class ShipmentInline(admin.TabularInline):
    model = Shipment
    extra = 0
    readonly_fields = ['loaded_at', 'delivered_at']

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['route_number', 'route_date', 'vehicle', 'driver', 'status']
    list_filter = ['status', 'route_date', 'tenant']
    search_fields = ['route_number', 'vehicle__plate_number']
    inlines = [ShipmentInline]

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['route', 'order', 'status', 'sequence', 'delivered_at']
    list_filter = ['status', 'route__route_date']
    search_fields = ['order__order_number', 'route__route_number']
