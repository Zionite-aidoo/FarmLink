from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Product


def cart_lines(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(pk__in=cart.keys(), status=Product.Status.ACTIVE, is_approved=True).select_related('category').prefetch_related('images')
    lines = []
    for product in products:
        try:
            quantity = Decimal(str(cart.get(str(product.pk), '0')))
        except InvalidOperation:
            continue
        if quantity <= 0:
            continue
        lines.append({'product': product, 'quantity': quantity, 'subtotal': product.price_per_kg * quantity})
    return lines


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, status=Product.Status.ACTIVE, is_approved=True)
    try:
        quantity = Decimal(request.POST.get('quantity', '1'))
    except InvalidOperation:
        quantity = Decimal('0')
    if quantity <= 0:
        messages.error(request, 'Enter a quantity greater than zero.')
        return redirect('catalog:detail', slug=product.slug)
    cart = request.session.get('cart', {})
    current = Decimal(str(cart.get(str(product.pk), '0')))
    if current + quantity > product.quantity_available:
        messages.error(request, 'That quantity is not currently available.')
    else:
        cart[str(product.pk)] = str(current + quantity)
        request.session['cart'] = cart
        messages.success(request, f'{product.name} added to your cart.')
    return redirect('cart:detail')


def cart_detail(request):
    lines = cart_lines(request)
    return render(request, 'cart/cart_detail.html', {'lines': lines, 'subtotal': sum((line['subtotal'] for line in lines), Decimal('0.00'))})


@require_POST
def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = Decimal(request.POST.get('quantity', '0'))
    except InvalidOperation:
        quantity = Decimal('0')
    if quantity <= 0:
        cart.pop(str(product_id), None)
    elif quantity <= product.quantity_available:
        cart[str(product_id)] = str(quantity)
    else:
        messages.error(request, 'That quantity is not currently available.')
    request.session['cart'] = cart
    return redirect('cart:detail')


@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart:detail')
