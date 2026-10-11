from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from apps.catalog.models import Category, Product

User = get_user_model()


class CartTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.farmer = User.objects.create_user(
            phone='+233241112233',
            full_name='Kwame Asante',
            role=User.Role.FARMER,
        )
        self.category = Category.objects.create(name='Vegetables', slug='vegetables')
        self.product = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Fresh Maize',
            price_per_kg=Decimal('5.00'),
            quantity_available=Decimal('20.00'),
            status=Product.Status.ACTIVE,
            is_approved=True,
        )

    def test_add_to_cart(self):
        response = self.client.post(reverse('cart:add', kwargs={'product_id': self.product.id}), {
            'quantity': '3.0',
        })
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)], '3.0')

    def test_add_to_cart_exceeds_stock(self):
        response = self.client.post(reverse('cart:add', kwargs={'product_id': self.product.id}), {
            'quantity': '25.0',
        })
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertNotIn('cart', session)

    def test_cart_detail_and_update(self):
        # Add item
        self.client.post(reverse('cart:add', kwargs={'product_id': self.product.id}), {'quantity': '2.0'})

        # View cart
        response = self.client.get(reverse('cart:detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fresh Maize')
        self.assertContains(response, 'GH₵ 10.00')

        # Update item
        self.client.post(reverse('cart:update', kwargs={'product_id': self.product.id}), {'quantity': '4.0'})
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)], '4.0')

        # Remove item
        self.client.post(reverse('cart:remove', kwargs={'product_id': self.product.id}))
        session = self.client.session
        self.assertNotIn(str(self.product.id), session['cart'])

