from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

SAMPLE_PRODUCTS = [
    {
        "name": "Fresh Maize",
        "price_per_kg": 5.00,
        "quantity_available": 200,
        "farmer_name": "Kwame Asante",
        "condition": "fresh",
        "is_negotiable": True,
    },
    {
        "name": "Ripe Tomatoes",
        "price_per_kg": 8.50,
        "quantity_available": 150,
        "farmer_name": "Ama Mensah",
        "condition": "ripe",
        "is_negotiable": True,
    },
    {
        "name": "White Yams",
        "price_per_kg": 12.00,
        "quantity_available": 80,
        "farmer_name": "Kofi Yeboah",
        "condition": "fresh",
        "is_negotiable": False,
    },
    {
        "name": "Cassava",
        "price_per_kg": 4.00,
        "quantity_available": 300,
        "farmer_name": "Akua Ofori",
        "condition": "fresh",
        "is_negotiable": True,
    },
    {
        "name": "Garden Eggs",
        "price_per_kg": 6.00,
        "quantity_available": 100,
        "farmer_name": "Yaw Adjei",
        "condition": "fresh",
        "is_negotiable": True,
    },
    {
        "name": "Ripe Plantain",
        "price_per_kg": 7.50,
        "quantity_available": 120,
        "farmer_name": "Esi Baiden",
        "condition": "ripe",
        "is_negotiable": False,
    },
    {
        "name": "Fresh Pepper (Shito)",
        "price_per_kg": 15.00,
        "quantity_available": 60,
        "farmer_name": "Kwame Asante",
        "condition": "fresh",
        "is_negotiable": True,
    },
    {
        "name": "Good Condition Oranges",
        "price_per_kg": 5.50,
        "quantity_available": 180,
        "farmer_name": "Nana Agyemang",
        "condition": "good",
        "is_negotiable": True,
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample products and a default admin user"

    def handle(self, *args, **options):
        # ── Admin user ──────────────────────────────────────────────
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@farmlink.com",
                password="admin123",
            )
            self.stdout.write(self.style.SUCCESS("Created superuser: admin / admin123"))
        else:
            self.stdout.write("Superuser 'admin' already exists — skipping.")

        # ── Products ────────────────────────────────────────────────
        existing = Product.objects.count()
        if existing > 0:
            self.stdout.write(
                f"Found {existing} existing product(s) — skipping seed."
            )
            return

        for data in SAMPLE_PRODUCTS:
            Product.objects.create(**data)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(SAMPLE_PRODUCTS)} sample products successfully!"
            )
        )

