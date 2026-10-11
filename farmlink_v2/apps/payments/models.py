from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Payment(models.Model):
    class Method(models.TextChoices):
        MTN_MOMO = 'mtn_momo', 'MTN Mobile Money'
        VODAFONE_CASH = 'vodafone_cash', 'Telecel Cash'
        AIRTELTIGO = 'airteltigo', 'AirtelTigo Money'
        CASH_ON_DELIVERY = 'cash_on_delivery', 'Cash on delivery'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Successful'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    order = models.OneToOneField('orders.Order', on_delete=models.PROTECT, related_name='payment')
    method = models.CharField(max_length=24, choices=Method.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    provider_reference = models.CharField(max_length=100, blank=True)
    payer_phone = models.CharField(max_length=20, blank=True)
    raw_callback = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.order.tracking_code} - {self.get_method_display()}'
