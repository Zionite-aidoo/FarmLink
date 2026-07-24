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
        "image_url": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=400&h=300&fit=crop",
    },
    {
        "name": "Ripe Tomatoes",
        "price_per_kg": 8.50,
        "quantity_available": 150,
        "farmer_name": "Ama Mensah",
        "condition": "ripe",
        "is_negotiable": True,
        "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400&h=300&fit=crop",
    },
    {
        "name": "Yams",
        "price_per_kg": 12.00,
        "quantity_available": 80,
        "farmer_name": "Kofi Yeboah",
        "condition": "fresh",
        "is_negotiable": False,
        "image_url": "https://images.unsplash.com/photo-1590168223692-6e02a0659b7d?w=400&h=300&fit=crop",
    },
    {
        "name": "Cassava",
        "price_per_kg": 4.00,
        "quantity_available": 300,
        "farmer_name": "Akua Ofori",
        "condition": "fresh",
        "is_negotiable": True,
        "image_url": "https://images.unsplash.com/photo-1595446761776-ef49d58d399b?w=400&h=300&fit=crop",
    },
    {
        "name": "Garden Eggs",
        "price_per_kg": 6.00,
        "quantity_available": 100,
        "farmer_name": "Yaw Adjei",
        "condition": "fresh",
        "is_negotiable": True,
        "image_url": "https://images.unsplash.com/photo-1608039829572-9b18dda7a49e?w=400&h=300&fit=crop",
    },
    {
        "name": "Ripe Plantain",
        "price_per_kg": 7.50,
        "quantity_available": 120,
        "farmer_name": "Esi Baiden",
        "condition": "ripe",
        "is_negotiable": False,
        "image_url": "https://images.unsplash.com/photo-1524781289445-ddf8f5695861?w=400&h=300&fit=crop",
    },
    {
        "name": "Unripe Plantain",
        "price_per_kg": 6.00,
        "quantity_available": 100,
        "farmer_name": "Esi Baiden",
        "condition": "fresh",
        "is_negotiable": True,
        "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6ba11d94?w=400&h=300&fit=crop",
    },
    {
        "name": "Fresh Pepper (Shito)",
        "price_per_kg": 15.00,
        "quantity_available": 60,
        "farmer_name": "Kwame Asante",
        "condition": "fresh",
        "is_negotiable": True,
        "image_url": "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400&h=300&fit=crop",
    },
    {
        "name": "Good Condition Oranges",
        "price_per_kg": 5.50,
        "quantity_available": 180,
        "farmer_name": "Nana Agyemang",
        "condition": "good",
        "is_negotiable": True,
        "image_url": "https://images.unsplash.com/photo-1582979512210-99b6a53386f9?w=400&h=300&fit=crop",
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
        if existing == 0:
            # Fresh seed — create everything
            for data in SAMPLE_PRODUCTS:
                Product.objects.create(**data)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Seeded {len(SAMPLE_PRODUCTS)} sample products successfully!"
                )
            )
        else:
            # Re-deploy: update existing products with image_url values
            # Also handle renamed products: "White Yams" → "Yams"
            old_name_map = {"White Yams": "Yams"}
            for old_name, new_name in old_name_map.items():
                old_products = Product.objects.filter(name=old_name)
                if old_products.exists():
                    # Check if "Yams" already exists
                    if not Product.objects.filter(name=new_name).exists():
                        old_products.update(name=new_name)
                        self.stdout.write(f"Renamed '{old_name}' → '{new_name}'")
                    else:
                        # "Yams" already exists — delete the old one
                        old_products.delete()
                        self.stdout.write(f"Deleted duplicate '{old_name}' (already have '{new_name}')")

            updated = 0
            created = 0
            for data in SAMPLE_PRODUCTS:
                name = data["name"]
                image_url = data.get("image_url", "")
                matched = Product.objects.filter(name=name)
                if matched.exists():
                    count = matched.update(image_url=image_url)
                    if count:
                        updated += count
                else:
                    Product.objects.create(**data)
                    created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {existing} existing product(s) — updated {updated} image_urls, created {created} new products."
                )
            )

