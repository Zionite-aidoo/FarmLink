from decimal import Decimal
import re
import sys

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.services import normalize_phone
from apps.cart.views import cart_lines
from apps.catalog.models import Product
from apps.payments.models import Payment
from apps.payments.providers import get_momo_provider
from .models import DeliveryZone, Order, OrderItem, OrderStatusHistory


@login_required
def checkout(request):
    lines = cart_lines(request)
    if not lines:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart:detail')
    subtotal = sum((line['subtotal'] for line in lines), Decimal('0.00'))
    zones = DeliveryZone.objects.filter(is_active=True)
    if request.method == 'POST':
        selected_zone = request.POST.get('zone', '')
        zone = DeliveryZone.objects.filter(pk=selected_zone, is_active=True).first()
        method = request.POST.get('method')
        valid_methods = {choice[0] for choice in Payment.Method.choices}
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        region = request.POST.get('region', '').strip()
        phone = normalize_phone(request.POST.get('phone') or request.user.phone)
        customer_name = request.POST.get('customer_name', '').strip() or request.user.full_name
        is_simulated_allowed = (settings.DEBUG or 'test' in sys.argv) and settings.PAYMENTS_MODE == 'simulated'
        if not zone or not address or not city or not re.fullmatch(r'\+[1-9]\d{7,14}', phone) or not customer_name or method not in valid_methods:
            messages.error(request, 'Complete all delivery details and choose a payment method.')
        elif method != Payment.Method.CASH_ON_DELIVERY and not is_simulated_allowed:
            messages.error(request, 'Live Mobile Money payments are not configured yet. Choose cash on delivery or use the development payment mode locally.')
        else:
            try:
                with transaction.atomic():
                    locked_lines = []
                    for line in lines:
                        product = Product.objects.select_for_update().get(pk=line['product'].pk)
                        quantity = line['quantity']
                        updated = Product.objects.filter(
                            pk=product.pk,
                            status=Product.Status.ACTIVE,
                            is_approved=True,
                            quantity_available__gte=quantity,
                        ).update(quantity_available=F('quantity_available') - quantity)
                        if not updated:
                            raise ValueError(f'{product.name} no longer has enough stock.')
                        locked_lines.append((product, quantity, product.price_per_kg * quantity))
                    total_subtotal = sum((item[2] for item in locked_lines), Decimal('0.00'))
                    order = Order.objects.create(
                        buyer=request.user,
                        customer_name=customer_name[:120],
                        phone=phone,
                        address=address,
                        city=city[:80],
                        region=region[:80],
                        zone=zone,
                        subtotal=total_subtotal,
                        delivery_fee=zone.fee,
                        total=total_subtotal + zone.fee,
                    )
                    for product, quantity, amount in locked_lines:
                        OrderItem.objects.create(
                            order=order, product=product, farmer=product.farmer,
                            product_name=product.name, price_per_kg=product.price_per_kg,
                            quantity_kg=quantity, subtotal=amount,
                        )
                    OrderStatusHistory.objects.create(order=order, status=order.status, note='Order placed')
                    payment = Payment.objects.create(
                        order=order, method=method, amount=order.total,
                        payer_phone=phone,
                    )
                    if method == Payment.Method.CASH_ON_DELIVERY:
                        payment.provider_reference = 'COD-' + order.tracking_code
                    else:
                        result = get_momo_provider().initiate(payment)
                        payment.status = result.status
                        payment.paid_at = result.paid_at
                        payment.provider_reference = result.reference
                        payment.raw_callback = result.callback or {}
                        if result.status == 'success':
                            order.status = Order.Status.CONFIRMED
                            order.save(update_fields=['status', 'updated_at'])
                            OrderStatusHistory.objects.create(order=order, status=Order.Status.CONFIRMED, note='Payment confirmed via Mobile Money')
                    payment.save(update_fields=['status', 'paid_at', 'provider_reference', 'raw_callback'])
            except Product.DoesNotExist:
                messages.error(request, 'A product in your cart is no longer available. Review your cart and try again.')
            except ValueError as error:
                messages.error(request, str(error))
            else:
                request.session['cart'] = {}
                return redirect('orders:success', tracking_code=order.tracking_code)
        return render(request, 'orders/checkout.html', {
            'lines': lines, 'subtotal': subtotal, 'zones': zones,
            'name': customer_name, 'phone': phone, 'address': address,
            'city': city, 'region': region,
            'selected_zone': selected_zone,
            'mobile_money_enabled': settings.DEBUG and settings.PAYMENTS_MODE == 'simulated',
        })
    return render(request, 'orders/checkout.html', {
        'lines': lines, 'subtotal': subtotal, 'zones': zones,
        'name': request.user.full_name, 'phone': request.user.phone,
        'city': request.user.city, 'region': request.user.region,
        'mobile_money_enabled': settings.DEBUG and settings.PAYMENTS_MODE == 'simulated',
    })


@login_required
def success(request, tracking_code):
    order = get_object_or_404(Order, tracking_code=tracking_code, buyer=request.user)
    return render(request, 'orders/success.html', {'order': order})


@login_required
def my_orders(request):
    orders = request.user.orders.prefetch_related('items', 'history', 'payment')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, tracking_code):
    order = get_object_or_404(Order.objects.prefetch_related('items', 'history').select_related('zone', 'payment'), tracking_code=tracking_code, buyer=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


def tracking(request):
    order = None
    if request.method == 'POST':
        code = request.POST.get('tracking_code', '').strip().upper()
        phone = normalize_phone(request.POST.get('phone'))
        order = Order.objects.filter(tracking_code=code, phone=phone).prefetch_related('items', 'history').select_related('zone').first()
        if not order:
            messages.error(request, 'We could not find an order with that tracking code and phone number.')
    return render(request, 'orders/tracking.html', {'order': order})
