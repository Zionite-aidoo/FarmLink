from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from apps.catalog.models import Category, Product

User = get_user_model()


class CatalogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.farmer = User.objects.create_user(
            phone='+233241112233',
            full_name='Kwame Asante',
            role=User.Role.FARMER,
        )
        self.category = Category.objects.create(name='Vegetables', slug='vegetables', icon='🥬')
        self.product = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Ripe Tomatoes',
            description='Freshly harvested plum tomatoes.',
            price_per_kg=Decimal('8.50'),
            quantity_available=Decimal('100.00'),
            unit='kg',
            condition=Product.Condition.RIPE,
            region='Greater Accra',
            city='Ada',
            status=Product.Status.ACTIVE,
            is_approved=True,
        )

    def test_product_slug_auto_generation(self):
        self.assertEqual(self.product.slug, 'ripe-tomatoes')

    def test_catalog_list_view(self):
        response = self.client.get(reverse('catalog:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ripe Tomatoes')
        self.assertContains(response, 'GH₵ 8.50')

    def test_catalog_search_and_filter(self):
        # Search match
        res1 = self.client.get(reverse('catalog:list'), {'q': 'Tomatoes'})
        self.assertContains(res1, 'Ripe Tomatoes')

        # Category match
        res2 = self.client.get(reverse('catalog:list'), {'category': 'vegetables'})
        self.assertContains(res2, 'Ripe Tomatoes')

        # Condition match
        res3 = self.client.get(reverse('catalog:list'), {'condition': 'ripe'})
        self.assertContains(res3, 'Ripe Tomatoes')

        # Mismatched condition
        res4 = self.client.get(reverse('catalog:list'), {'condition': 'fresh'})
        self.assertNotContains(res4, 'Ripe Tomatoes')

    def test_product_detail_view(self):
        response = self.client.get(reverse('catalog:detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ripe Tomatoes')
        self.assertContains(response, 'Kwame Asante')

    def test_unapproved_product_hidden_from_public(self):
        unapproved = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Hidden Produce',
            price_per_kg=Decimal('10.00'),
            quantity_available=Decimal('50.00'),
            status=Product.Status.ACTIVE,
            is_approved=False,
        )
        response = self.client.get(reverse('catalog:detail', kwargs={'slug': unapproved.slug}))
        self.assertEqual(response.status_code, 404)

