from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from apps.catalog.models import Category, Product
from apps.orders.models import DeliveryZone, Order, OrderItem
from apps.payments.models import Payment

User = get_user_model()


class DashboardTests(TestCase):
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
        self.category = Category.objects.create(name='Fruits', slug='fruits')
        self.zone = DeliveryZone.objects.create(
            name='Accra Metro',
            fee=Decimal('25.00'),
            estimated_window='Same day',
            is_active=True,
        )

    def test_buyer_dashboard(self):
        self.client.force_login(self.buyer)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your farm')

    def test_farmer_permission_required(self):
        self.client.force_login(self.buyer)
        response = self.client.get(reverse('dashboard:farmer'))
        self.assertEqual(response.status_code, 403)

    def test_farmer_dashboard_and_product_create(self):
        self.client.force_login(self.farmer)
        # Farmer home
        response = self.client.get(reverse('dashboard:farmer'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kwame Asante')

        # Product create
        create_res = self.client.post(reverse('dashboard:product_create'), {
            'category': self.category.id,
            'name': 'Pineapples',
            'description': 'Sugarloaf pineapples.',
            'price_per_kg': '15.00',
            'quantity_available': '50.00',
            'unit': 'kg',
            'condition': 'fresh',
            'region': 'Eastern',
            'city': 'Nsawam',
            'status': 'active',
        })
        self.assertEqual(create_res.status_code, 302)
        created = Product.objects.get(name='Pineapples')
        self.assertEqual(created.farmer, self.farmer)
        self.assertFalse(created.is_approved)  # Moderation workflow

    def test_farmer_advance_order(self):
        self.client.force_login(self.farmer)
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
            status=Order.Status.PENDING,
        )
        product = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Oranges',
            price_per_kg=Decimal('5.00'),
            quantity_available=Decimal('50.00'),
            status=Product.Status.ACTIVE,
            is_approved=True,
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            farmer=self.farmer,
            product_name='Oranges',
            price_per_kg=Decimal('5.00'),
            quantity_kg=Decimal('10.00'),
            subtotal=Decimal('50.00'),
        )
        Payment.objects.create(
            order=order,
            method=Payment.Method.CASH_ON_DELIVERY,
            amount=Decimal('75.00'),
            status=Payment.Status.PENDING,
        )

        # Advance order: PENDING -> CONFIRMED
        advance_res = self.client.post(reverse('dashboard:advance_order', kwargs={'pk': order.pk}))
        self.assertEqual(advance_res.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CONFIRMED)
