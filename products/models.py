from django.db import models
from django.db.models import JSONField
import json

class Product(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.IntegerField()
    farmer_name = models.CharField(max_length=200)
    condition = models.CharField(
        max_length=10,
        choices=[
            ('fresh', 'Fresh'),
            ('good', 'Good'),
            ('ripe', 'Ripe'),
        ],
        default='fresh',
    )
    is_negotiable = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Products"

class Order(models.Model):
    # Payment workflow (simulated)
    class PaymentMethod(models.TextChoices):
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'
        CASH_ON_DELIVERY = 'cash_on_delivery', 'Cash on Delivery'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'

    # Fulfillment workflow
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PREPARING = 'preparing', 'Preparing'
        OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    customer_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    # Snapshot of {"product_id": quantity_kg}
    # Allow empty on creation so Django admin "add" doesn't crash.
    items = JSONField(default=dict, blank=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment/order workflow
    payment_method = models.CharField(
        max_length=40,
        choices=PaymentMethod.choices,
        default=PaymentMethod.MOBILE_MONEY,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    order_status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )

    # When payment is simulated successfully
    paid_at = models.DateTimeField(blank=True, null=True)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"



