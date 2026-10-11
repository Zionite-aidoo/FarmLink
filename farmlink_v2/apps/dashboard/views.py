from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.catalog.models import Product, ProductImage
from apps.orders.models import Order, OrderStatusHistory
from .forms import ProductForm


@login_required
def home(request):
    if request.user.can_sell:
        return redirect('dashboard:farmer')
    orders = request.user.orders.order_by('-created_at')[:5]
    return render(request, 'dashboard/buyer_home.html', {'orders': orders})


@login_required
def farmer_home(request):
    if not request.user.can_sell:
        return HttpResponseForbidden('Farmer access required.')
    products = Product.objects.filter(farmer=request.user)
    order_items = request.user.sales_items.select_related('order').filter(
        order__status__in=[Order.Status.PENDING, Order.Status.CONFIRMED, Order.Status.PREPARING, Order.Status.OUT_FOR_DELIVERY]
    )
    delivered_sales = request.user.sales_items.filter(order__status=Order.Status.DELIVERED).aggregate(total=Sum('subtotal'))['total'] or Decimal('0.00')
    return render(request, 'dashboard/farmer_home.html', {
        'products_count': products.count(),
        'active_products': products.filter(status=Product.Status.ACTIVE, is_approved=True).count(),
        'pending_products': products.filter(is_approved=False).count(),
        'low_stock': products.filter(quantity_available__lte=5, status=Product.Status.ACTIVE).count(),
        'incoming_items': order_items.order_by('-order__created_at')[:8],
        'delivered_sales': delivered_sales,
    })


@login_required
def farmer_products(request):
    if not request.user.can_sell:
        return HttpResponseForbidden('Farmer access required.')
    products = Product.objects.filter(farmer=request.user).select_related('category')
    return render(request, 'dashboard/farmer_products.html', {'products': products})


@login_required
def product_create(request):
    if not request.user.can_sell:
        return HttpResponseForbidden('Farmer access required.')
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.farmer = request.user
        product.is_approved = False
        product.region = product.region or request.user.region
        product.city = product.city or request.user.city
        product.save()
        for image in form.cleaned_data.get('images', []):
            ProductImage.objects.create(product=product, image=image, alt=product.name)
        messages.success(request, 'Produce saved and submitted for review before it appears in the marketplace.')
        return redirect('dashboard:products')
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Add produce'})


@login_required
def product_edit(request, pk):
    if not request.user.can_sell:
        return HttpResponseForbidden('Farmer access required.')
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.is_approved = False
        product.save()
        for image in form.cleaned_data.get('images', []):
            ProductImage.objects.create(product=product, image=image, alt=product.name)
        messages.success(request, 'Produce updated and returned to review before it appears in the marketplace.')
        return redirect('dashboard:products')
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': f'Edit {product.name}', 'product': product})


@login_required
@require_POST
def product_delete(request, pk):
    if not request.user.can_sell:
        return HttpResponseForbidden('Farmer access required.')
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    product.delete()
    messages.success(request, 'Produce listing removed.')
    return redirect('dashboard:products')


@login_required
def farmer_orders(request):
    if not request.user.can_sell:
        return HttpResponseForbidden('Farmer access required.')
    orders = Order.objects.filter(items__farmer=request.user).select_related('buyer', 'zone').prefetch_related('items', 'history').distinct()
    return render(request, 'dashboard/farmer_orders.html', {'orders': orders})


@login_required
@require_POST
def advance_order(request, pk):
    if not request.user.can_sell:
        return HttpResponseForbidden('Farmer access required.')
    order = get_object_or_404(Order.objects.filter(items__farmer=request.user).distinct(), pk=pk)
    transitions = {
        Order.Status.PENDING: Order.Status.CONFIRMED,
        Order.Status.CONFIRMED: Order.Status.PREPARING,
        Order.Status.PREPARING: Order.Status.OUT_FOR_DELIVERY,
        Order.Status.OUT_FOR_DELIVERY: Order.Status.DELIVERED,
    }
    next_status = transitions.get(order.status)
    if next_status:
        order.status = next_status
        order.save(update_fields=['status', 'updated_at'])
        OrderStatusHistory.objects.create(order=order, status=next_status, note=f'Updated by {request.user.full_name}')
        if next_status == Order.Status.DELIVERED and order.payment.method == 'cash_on_delivery':
            order.payment.status = 'success'
            order.payment.paid_at = timezone.now()
            order.payment.save(update_fields=['status', 'paid_at'])
        messages.success(request, f'Order {order.tracking_code} updated to {order.get_status_display().lower()}.')
    else:
        messages.error(request, 'This order can no longer be advanced.')
    return redirect('dashboard:orders')


@login_required
def profile(request):
    if request.method == 'POST':
        request.user.full_name = request.POST.get('full_name', '').strip()[:120]
        request.user.city = request.POST.get('city', '').strip()[:80]
        request.user.region = request.POST.get('region', '').strip()[:80]
        if request.user.full_name:
            request.user.save(update_fields=['full_name', 'city', 'region'])
            messages.success(request, 'Your profile has been updated.')
            return redirect('dashboard:profile')
        messages.error(request, 'Your name is required.')
    return render(request, 'dashboard/profile.html')
