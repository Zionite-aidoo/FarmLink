from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
from .models import Product, Order


def home(request):
    """Homepage with landing content"""
    products = Product.objects.all()[:6]  # Featured products
    context = {'featured_products': products}
    return render(request, 'home.html', context)

def product_list(request):
    """List all products in grid"""
    products = Product.objects.all().order_by('-created_at')
    context = {'products': products}
    return render(request, 'products_list.html', context)

def product_detail(request, pk):
    """Product detail page"""
    product = get_object_or_404(Product, pk=pk)
    context = {'product': product}
    return render(request, 'product_detail.html', context)


def about(request):
    """About/landing page"""
    return render(request, 'about.html')


def contact(request):
    """Dedicated Contact page"""
    return render(request, 'contact.html')



@require_http_methods(["POST"])
def cart_add(request, pk):
    """Add product to cart session"""
    product = get_object_or_404(Product, pk=pk)
    quantity = int(request.POST.get('quantity', 1))
    
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + quantity
    if cart[str(pk)] > product.quantity_available:
        messages.error(request, f'Only {product.quantity_available} available!')
        return redirect('product_detail', pk=pk)
    
    request.session['cart'] = cart
    messages.success(request, f'Added {quantity}kg {product.name} to cart!')
    return redirect('product_detail', pk=pk)

def cart_view(request):
    """View cart contents"""
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    
    cart_items = []
    total = Decimal('0.00')
    
    for product in products:
        qty = cart[str(product.id)]
        subtotal = product.price_per_kg * Decimal(qty)
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal,
        })
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'cart.html', context)

@require_http_methods(["POST"])
def cart_update(request, pk):
    """Update cart item quantity"""
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 0))
    
    if quantity == 0:
        cart.pop(str(pk), None)
    else:
        cart[str(pk)] = quantity
    
    request.session['cart'] = cart
    return redirect('cart')

def checkout(request):
    """Checkout form"""
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    
    cart_items = []
    total = Decimal('0.00')
    
    for product in products:
        qty = cart[str(product.id)]
        subtotal = product.price_per_kg * Decimal(qty)
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': qty,
            'subtotal': subtotal,
        })
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    
    if request.method == 'POST':
        if not cart:
            messages.error(request, 'Cart is empty!')
            return redirect('cart')
        
        items_data = {str(product.id): item['quantity'] for item in cart_items}
        
        # Simulate successful payment during checkout
        payment_method = request.POST.get('payment_method', Order.PaymentMethod.MOBILE_MONEY)

        # Generate a fake transaction reference (no external API calls)
        # Example: TX-20260507-483921
        import random
        transaction_reference = f"TX-{timezone.now().strftime('%Y%m%d')}-{random.randint(100000, 999999)}"

        order = Order.objects.create(
            customer_name=request.POST['customer_name'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            items=items_data,
            total_price=total,
            payment_method=payment_method,
            payment_status=Order.PaymentStatus.PAID,
            order_status=Order.OrderStatus.PENDING,
            paid_at=timezone.now(),
            transaction_reference=transaction_reference,
        )



        del request.session['cart']
        messages.success(request, 'Order placed successfully!')
        return redirect('order_success', order_id=order.id)




    return render(request, 'checkout.html', context)


def order_success(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    return render(request, 'order_success.html', context)


@require_http_methods(["GET", "POST"])
def order_lookup(request):
    """Order lookup page by phone number (beginner-friendly, no auth required)."""
    if request.method == 'POST':
        phone = (request.POST.get('phone') or '').strip()
        if not phone:
            messages.error(request, 'Please enter your phone number.')
            return redirect('order_lookup')

        # Phone-number lookup: show all orders that match this phone.
        orders = Order.objects.filter(phone=phone).order_by('-created_at')
        return render(request, 'order_lookup.html', {
            'lookup_phone': phone,
            'orders': orders,
        })

    return render(request, 'order_lookup.html', {
        'lookup_phone': '',
        'orders': None,
    })


