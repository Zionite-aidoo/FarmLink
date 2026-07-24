from django.contrib import admin
from .models import Product, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'image_url', 'farmer_name', 'price_per_kg', 'quantity_available', 'condition', 'is_negotiable', 'created_at')
    list_filter = ('farmer_name', 'condition', 'is_negotiable', 'created_at')
    search_fields = ('name', 'farmer_name')
    readonly_fields = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_name',
        'phone',
        'total_price',
        'payment_status',
        'order_status',
        'payment_method',
        'transaction_reference',
        'created_at',
    )
    list_filter = ('created_at', 'payment_status', 'order_status', 'payment_method')
    search_fields = ('customer_name', 'phone', 'transaction_reference')
    readonly_fields = ('items', 'created_at', 'paid_at', 'transaction_reference')

    # Allow staff to move the order through fulfillment stages
    fieldsets = (
        ('Customer', {'fields': ('customer_name', 'phone', 'address')}),
        ('Order Summary', {'fields': ('items', 'total_price')}),
        ('Workflow', {'fields': ('payment_method', 'payment_status', 'order_status', 'paid_at', 'transaction_reference')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )

