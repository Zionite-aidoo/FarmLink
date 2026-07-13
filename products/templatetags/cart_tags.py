from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def cart_total(request):
    cart = request.session.get('cart', {})
    if not cart:
        return mark_safe('0.00')
    
    from decimal import Decimal
    from products.models import Product
    products = Product.objects.filter(id__in=cart.keys())
    total = Decimal('0.00')
    for product in products:
        qty = cart[str(product.id)]
        total += product.price_per_kg * Decimal(qty)
    
    return mark_safe(f'{total:.2f}')

