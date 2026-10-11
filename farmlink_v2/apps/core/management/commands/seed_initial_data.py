from decimal import Decimal
import os
import shutil
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.catalog.models import Category, Product, ProductImage
from apps.orders.models import DeliveryZone, Order, OrderItem, OrderStatusHistory
from apps.payments.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = 'Create starter categories, delivery zones, verified Ghanaian farmers, produce, and demo orders.'

    def handle(self, *args, **options):
        # 1. Categories
        categories_data = [
            ('Vegetables', '🥬'),
            ('Fruits', '🍍'),
            ('Roots & tubers', '🍠'),
            ('Grains & legumes', '🌾'),
            ('Herbs & spices', '🌶️'),
        ]
        category_map = {}
        for position, (name, icon) in enumerate(categories_data):
            cat, _ = Category.objects.update_or_create(
                name=name,
                defaults={'slug': slugify(name), 'icon': icon, 'ordering': position},
            )
            category_map[name] = cat
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(category_map)} categories.'))

        # 2. Delivery Zones
        zones_data = [
            ('Accra Metro', '25.00', 'Same day / next day'),
            ('Tema & Ashaiman', '30.00', '1-2 days'),
            ('Kumasi Metro', '25.00', 'Same day / next day'),
            ('Other Greater Accra', '40.00', '2-3 days'),
            ('Central Region (Kasoa/Winneba)', '35.00', '1-2 days'),
        ]
        zone_map = {}
        for name, fee, window in zones_data:
            z, _ = DeliveryZone.objects.update_or_create(
                name=name,
                defaults={'fee': Decimal(fee), 'estimated_window': window, 'is_active': True},
            )
            zone_map[name] = z
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(zone_map)} delivery zones.'))

        # 3. Superuser
        admin_user, _ = User.objects.get_or_create(
            phone='+233200000001',
            defaults={
                'full_name': 'FarmLink Admin',
                'role': User.Role.BOTH,
                'region': 'Greater Accra',
                'city': 'Accra',
                'is_staff': True,
                'is_superuser': True,
                'is_phone_verified': True,
            },
        )

        # 4. Ghanaian Farmers
        farmers_data = [
            {
                'phone': '+233241112233',
                'full_name': 'Kwame Asante',
                'role': User.Role.FARMER,
                'region': 'Ashanti',
                'city': 'Ejura',
            },
            {
                'phone': '+233242223344',
                'full_name': 'Ama Mensah',
                'role': User.Role.FARMER,
                'region': 'Greater Accra',
                'city': 'Ada',
            },
            {
                'phone': '+233243334455',
                'full_name': 'Kofi Yeboah',
                'role': User.Role.FARMER,
                'region': 'Eastern',
                'city': 'Begoro',
            },
            {
                'phone': '+233244445566',
                'full_name': 'Akua Ofori',
                'role': User.Role.FARMER,
                'region': 'Central',
                'city': 'Bawjiase',
            },
            {
                'phone': '+233245556677',
                'full_name': 'Nana Agyemang',
                'role': User.Role.FARMER,
                'region': 'Eastern',
                'city': 'Suhum',
            },
        ]
        farmer_map = {}
        for fd in farmers_data:
            farmer, _ = User.objects.update_or_create(
                phone=fd['phone'],
                defaults={
                    'full_name': fd['full_name'],
                    'role': fd['role'],
                    'region': fd['region'],
                    'city': fd['city'],
                    'is_phone_verified': True,
                    'is_active': True,
                },
            )
            farmer_map[fd['full_name']] = farmer
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(farmer_map)} local farmers.'))

        # 5. Demo Buyer
        buyer_user, _ = User.objects.update_or_create(
            phone='+233249998877',
            defaults={
                'full_name': 'Abena Serwaa',
                'role': User.Role.BUYER,
                'region': 'Greater Accra',
                'city': 'Osu, Accra',
                'is_phone_verified': True,
                'is_active': True,
            },
        )

        # 6. Ensure media directory and product images are in place
        media_products_dir = os.path.join(settings.MEDIA_ROOT, 'catalog', 'products')
        os.makedirs(media_products_dir, exist_ok=True)

        static_images_dir = os.path.join(settings.BASE_DIR, 'static', 'product_images')
        root_static_images = os.path.join(settings.BASE_DIR.parent, 'static', 'product_images')

        for img_src_dir in [static_images_dir, root_static_images]:
            if os.path.exists(img_src_dir):
                for fname in os.listdir(img_src_dir):
                    src_file = os.path.join(img_src_dir, fname)
                    dst_file = os.path.join(media_products_dir, fname)
                    if os.path.isfile(src_file) and not os.path.exists(dst_file):
                        shutil.copy2(src_file, dst_file)

        # 7. Products catalog
        products_data = [
            {
                'farmer': farmer_map['Kwame Asante'],
                'category': category_map['Grains & legumes'],
                'name': 'Fresh Yellow Maize',
                'description': 'Crisp, organically grown yellow corn harvested fresh from our Ejura fields. High nutritional content and ideal for both domestic cooking and feed.',
                'price_per_kg': Decimal('5.50'),
                'quantity_available': Decimal('350.00'),
                'unit': 'kg',
                'condition': Product.Condition.FRESH,
                'is_negotiable': True,
                'region': 'Ashanti',
                'city': 'Ejura',
                'image_name': 'maize.jpg',
            },
            {
                'farmer': farmer_map['Ama Mensah'],
                'category': category_map['Vegetables'],
                'name': 'Ripe Roma Tomatoes',
                'description': 'Farm-ripe Ghanaian plum tomatoes from Ada Foah. Juicy, firm, and harvested this morning. Perfect for rich tomato stew and fresh salads.',
                'price_per_kg': Decimal('8.50'),
                'quantity_available': Decimal('180.00'),
                'unit': 'kg',
                'condition': Product.Condition.RIPE,
                'is_negotiable': True,
                'region': 'Greater Accra',
                'city': 'Ada',
                'image_name': 'tomatoes.jpg',
            },
            {
                'farmer': farmer_map['Kofi Yeboah'],
                'category': category_map['Roots & tubers'],
                'name': 'Premium Pona Yams',
                'description': 'Real Pona yams from the highlands of Begoro. Soft, sweet, and cook to perfection in under 20 minutes.',
                'price_per_kg': Decimal('12.00'),
                'quantity_available': Decimal('120.00'),
                'unit': 'kg',
                'condition': Product.Condition.FRESH,
                'is_negotiable': False,
                'region': 'Eastern',
                'city': 'Begoro',
                'image_name': 'yams.jpg',
            },
            {
                'farmer': farmer_map['Akua Ofori'],
                'category': category_map['Roots & tubers'],
                'name': 'Fresh White Cassava',
                'description': 'High-starch white cassava fresh from the farm. Ideal for banku, fufu, or gari processing.',
                'price_per_kg': Decimal('4.50'),
                'quantity_available': Decimal('400.00'),
                'unit': 'kg',
                'condition': Product.Condition.FRESH,
                'is_negotiable': True,
                'region': 'Central',
                'city': 'Bawjiase',
                'image_name': 'cassava.jpg',
            },
            {
                'farmer': farmer_map['Ama Mensah'],
                'category': category_map['Vegetables'],
                'name': 'Fresh Garden Eggs',
                'description': 'Tender, bright garden eggs (aubergines) harvested at peak tenderness. Great for abom and traditional soups.',
                'price_per_kg': Decimal('6.00'),
                'quantity_available': Decimal('150.00'),
                'unit': 'kg',
                'condition': Product.Condition.FRESH,
                'is_negotiable': True,
                'region': 'Greater Accra',
                'city': 'Ada',
                'image_name': 'garden-eggs.jpg',
            },
            {
                'farmer': farmer_map['Akua Ofori'],
                'category': category_map['Fruits'],
                'name': 'Sweet Ripe Plantain',
                'description': 'Golden sweet plantains picked right on time. Soft, sweet, and ready for kelewele, tatale, or red red.',
                'price_per_kg': Decimal('7.50'),
                'quantity_available': Decimal('200.00'),
                'unit': 'kg',
                'condition': Product.Condition.RIPE,
                'is_negotiable': False,
                'region': 'Central',
                'city': 'Bawjiase',
                'image_name': 'plantain.jpg',
            },
            {
                'farmer': farmer_map['Akua Ofori'],
                'category': category_map['Fruits'],
                'name': 'Green Cooking Plantain',
                'description': 'Firm green plantains ideal for fufu, plantain chips, or boiled ampesi with kontomire stew.',
                'price_per_kg': Decimal('6.50'),
                'quantity_available': Decimal('160.00'),
                'unit': 'kg',
                'condition': Product.Condition.FRESH,
                'is_negotiable': True,
                'region': 'Central',
                'city': 'Bawjiase',
                'image_name': 'unripe-plantain.jpg',
            },
            {
                'farmer': farmer_map['Kwame Asante'],
                'category': category_map['Herbs & spices'],
                'name': 'Fresh Green & Red Shito Pepper',
                'description': 'Pungent, highly aromatic Ghanaian chili peppers. Packed with fiery heat and authentic aroma for fresh pepper sauce.',
                'price_per_kg': Decimal('16.00'),
                'quantity_available': Decimal('85.00'),
                'unit': 'kg',
                'condition': Product.Condition.FRESH,
                'is_negotiable': True,
                'region': 'Ashanti',
                'city': 'Ejura',
                'image_name': 'pepper.jpg',
            },
            {
                'farmer': farmer_map['Nana Agyemang'],
                'category': category_map['Fruits'],
                'name': 'Juicy Sweet Oranges',
                'description': 'Naturally sun-ripened citrus oranges from Suhum orchards. High juice yield, sweet flavor, no artificial waxes.',
                'price_per_kg': Decimal('6.00'),
                'quantity_available': Decimal('240.00'),
                'unit': 'kg',
                'condition': Product.Condition.GOOD,
                'is_negotiable': True,
                'region': 'Eastern',
                'city': 'Suhum',
                'image_name': 'oranges.jpg',
            },
        ]

        created_products = []
        for pd in products_data:
            image_name = pd.pop('image_name')
            p, created = Product.objects.update_or_create(
                name=pd['name'],
                farmer=pd['farmer'],
                defaults={
                    'category': pd['category'],
                    'description': pd['description'],
                    'price_per_kg': pd['price_per_kg'],
                    'quantity_available': pd['quantity_available'],
                    'unit': pd['unit'],
                    'condition': pd['condition'],
                    'is_negotiable': pd['is_negotiable'],
                    'region': pd['region'],
                    'city': pd['city'],
                    'status': Product.Status.ACTIVE,
                    'is_approved': True,
                },
            )
            created_products.append(p)

            # Link ProductImage
            img_rel_path = f'catalog/products/{image_name}'
            if not p.images.exists():
                ProductImage.objects.create(
                    product=p,
                    image=img_rel_path,
                    alt=p.name,
                    ordering=0,
                )

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(created_products)} produce items with photos.'))

        # 8. Seed sample orders so dashboards and tracking have live data
        sample_order, o_created = Order.objects.get_or_create(
            tracking_code='FL-ACCRA1',
            defaults={
                'buyer': buyer_user,
                'customer_name': 'Abena Serwaa',
                'phone': '+233249998877',
                'address': 'House 14, 5th Lane, Osu RE',
                'city': 'Accra',
                'region': 'Greater Accra',
                'zone': zone_map['Accra Metro'],
                'subtotal': Decimal('67.00'),
                'delivery_fee': Decimal('25.00'),
                'total': Decimal('92.00'),
                'status': Order.Status.PREPARING,
            },
        )
        if o_created:
            p_tomatoes = Product.objects.get(name='Ripe Roma Tomatoes')
            p_plantain = Product.objects.get(name='Sweet Ripe Plantain')
            p_pepper = Product.objects.get(name='Fresh Green & Red Shito Pepper')

            OrderItem.objects.create(
                order=sample_order,
                product=p_tomatoes,
                farmer=p_tomatoes.farmer,
                product_name=p_tomatoes.name,
                price_per_kg=p_tomatoes.price_per_kg,
                quantity_kg=Decimal('4.00'),
                subtotal=Decimal('34.00'),
            )
            OrderItem.objects.create(
                order=sample_order,
                product=p_plantain,
                farmer=p_plantain.farmer,
                product_name=p_plantain.name,
                price_per_kg=p_plantain.price_per_kg,
                quantity_kg=Decimal('2.00'),
                subtotal=Decimal('15.00'),
            )
            OrderItem.objects.create(
                order=sample_order,
                product=p_pepper,
                farmer=p_pepper.farmer,
                product_name=p_pepper.name,
                price_per_kg=p_pepper.price_per_kg,
                quantity_kg=Decimal('1.125'),
                subtotal=Decimal('18.00'),
            )

            OrderStatusHistory.objects.create(
                order=sample_order,
                status=Order.Status.PENDING,
                note='Order received from buyer',
            )
            OrderStatusHistory.objects.create(
                order=sample_order,
                status=Order.Status.CONFIRMED,
                note='Payment confirmed via MTN Mobile Money',
            )
            OrderStatusHistory.objects.create(
                order=sample_order,
                status=Order.Status.PREPARING,
                note='Farmers are packaging harvest for delivery',
            )

            Payment.objects.create(
                order=sample_order,
                method=Payment.Method.MTN_MOMO,
                amount=Decimal('92.00'),
                status=Payment.Status.SUCCESS,
                provider_reference='SIM-MOMO-83921',
                payer_phone='+233249998877',
                paid_at=timezone.now(),
            )
            self.stdout.write(self.style.SUCCESS('Seeded sample active order FL-ACCRA1 for demonstration.'))

        self.stdout.write(self.style.SUCCESS('\n>>> FarmLink v2 is fully seeded and ready for action! <<<'))

