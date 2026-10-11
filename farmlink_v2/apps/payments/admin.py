from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'amount', 'status', 'provider_reference', 'paid_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('order__tracking_code', 'provider_reference', 'payer_phone')
    readonly_fields = ('order', 'method', 'amount', 'status', 'provider_reference', 'payer_phone', 'raw_callback', 'paid_at', 'created_at')
