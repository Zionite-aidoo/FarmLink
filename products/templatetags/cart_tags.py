from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Emoji map for product names — fallback to first letter if not found
PRODUCT_EMOJI_MAP = {
    'maize': '🌽',
    'tomatoes': '🍅',
    'tomato': '🍅',
    'yams': '🍠',
    'yam': '🍠',
    'cassava': '🥔',
    'garden eggs': '🥬',
    'garden egg': '🥬',
    'plantain': '🍌',
    'pepper': '🌶️',
    'oranges': '🍊',
    'orange': '🍊',
    'banana': '🍌',
    'cabbage': '🥬',
    'carrot': '🥕',
    'lettuce': '🥬',
    'onion': '🧅',
    'garlic': '🧄',
    'ginger': '🫚',
    'pineapple': '🍍',
    'mango': '🥭',
    'coconut': '🥥',
    'cocoyam': '🍠',
    'sweet potato': '🍠',
    'pumpkin': '🎃',
    'okro': '🫘',
    'beans': '🫘',
    'rice': '🍚',
    'egg': '🥚',
    'fish': '🐟',
    'chicken': '🐔',
    'soya': '🫘',
    'soybean': '🫘',
    'groundnut': '🥜',
    'peanut': '🥜',
}

# Background colors for product cards (warm, natural tones)
PRODUCT_COLORS = [
    '#fef3c7',  # warm yellow
    '#d1fae5',  # mint
    '#fce7f3',  # pink
    '#dbedfb',  # sky blue
    '#fde68a',  # amber
    '#d9f99d',  # lime
    '#fecaca',  # red
    '#c7d2fe',  # indigo
    '#fbcfe8',  # rose
    '#a7f3d0',  # emerald
]


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


@register.simple_tag
def product_emoji(product):
    """Return a colorful emoji for a given product."""
    name_lower = product.name.lower().strip()
    # Check full name first, then individual words
    if name_lower in PRODUCT_EMOJI_MAP:
        return mark_safe(PRODUCT_EMOJI_MAP[name_lower])
    for word in name_lower.split():
        if word in PRODUCT_EMOJI_MAP:
            return mark_safe(PRODUCT_EMOJI_MAP[word])
    # Fallback: return first letter
    return mark_safe(product.name[0].upper())


@register.simple_tag
def product_color(product):
    """Return a consistent background color for a product based on its ID."""
    idx = product.id % len(PRODUCT_COLORS)
    return PRODUCT_COLORS[idx]


@register.simple_tag
def product_card_style(product):
    """Return inline style for the product image placeholder."""
    emoji = product_emoji(product)
    bg = product_color(product)
    return mark_safe(f'background: {bg}; font-size: 4.5rem; display: flex; align-items: center; justify-content: center;')

