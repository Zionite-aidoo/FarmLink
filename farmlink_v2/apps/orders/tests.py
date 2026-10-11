from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from apps.catalog.models import Category, Product
from apps.orders.models import DeliveryZone, Order, OrderItem
from apps.payments.models import Payment

User = get_user_model()


class OrdersTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.farmer = User.objects.create_user(
            phone='+233241112233',
            full_name='Kwame Asante',
            role=User.Role.FARMER,
        )
        self.buyer = User.objects.create_user(
            phone='+233249998877',
            full_name='Abena Serwaa',
            role=User.Role.BUYER,
        )
        self.category = Category.objects.create(name='Tubers', slug='tubers')
        self.product = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Pona Yams',
            price_per_kg=Decimal('10.00'),
            quantity_available=Decimal('20.00'),
            status=Product.Status.ACTIVE,
            is_approved=True,
        )
        self.zone = DeliveryZone.objects.create(
            name='Accra Metro',
            fee=Decimal('25.00'),
            estimated_window='Same day',
            is_active=True,
        )

    def test_checkout_flow(self):
        self.client.force_login(self.buyer)

        # Add to cart
        self.client.post(reverse('cart:add', kwargs={'product_id': self.product.id}), {'quantity': '5.0'})

        # Post checkout form
        response = self.client.post(reverse('orders:checkout'), {
            'customer_name': 'Abena Serwaa',
            'phone': '0249998877',
            'address': 'House 12, Osu',
            'city': 'Accra',
            'region': 'Greater Accra',
            'zone': self.zone.id,
            'method': Payment.Method.MTN_MOMO,
        })
        self.assertEqual(response.status_code, 302)

        # Verify stock was decremented atomically
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity_available, Decimal('15.00'))

        # Verify order exists
        order = Order.objects.filter(buyer=self.buyer).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.subtotal, Decimal('50.00'))
        self.assertEqual(order.delivery_fee, Decimal('25.00'))
        self.assertEqual(order.total, Decimal('75.00'))
        self.assertEqual(order.status, Order.Status.CONFIRMED)

        # Verify order item snapshot
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.product_name, 'Pona Yams')
        self.assertEqual(item.quantity_kg, Decimal('5.00'))

        # Verify payment
        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.status, Payment.Status.SUCCESS)

    def test_tracking_view(self):
        order = Order.objects.create(
            buyer=self.buyer,
            customer_name='Abena Serwaa',
            phone='+233249998877',
            address='123 Road',
            city='Accra',
            zone=self.zone,
            subtotal=Decimal('50.00'),
            delivery_fee=Decimal('25.00'),
            total=Decimal('75.00'),
        )
        response = self.client.post(reverse('orders:tracking'), {
            'tracking_code': order.tracking_code,
            'phone': '0249998877',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.tracking_code)

