from django.contrib import admin
from .models import DeliveryZone, Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'farmer', 'product_name', 'price_per_kg', 'quantity_kg', 'subtotal')


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status', 'note', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'customer_name', 'phone', 'status', 'total', 'created_at')
    list_filter = ('status', 'zone', 'created_at')
    search_fields = ('tracking_code', 'customer_name', 'phone', 'buyer__phone')
    readonly_fields = ('tracking_code', 'created_at', 'updated_at')
    inlines = [OrderItemInline, OrderStatusHistoryInline]


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'fee', 'estimated_window', 'is_active')
    list_editable = ('fee', 'estimated_window', 'is_active')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'note', 'created_at')
    list_filter = ('status', 'created_at')
