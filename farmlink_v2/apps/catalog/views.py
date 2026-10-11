from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_queryset():
    return Product.objects.filter(status=Product.Status.ACTIVE, is_approved=True, quantity_available__gt=0).select_related('category', 'farmer').prefetch_related('images')


def home(request):
    featured = product_queryset()[:8]
    return render(request, 'core/home.html', {
        'featured_products': featured,
        'categories': Category.objects.all()[:8],
        'farmer_count': Product.objects.filter(status='active', is_approved=True).values('farmer_id').distinct().count(),
    })


def product_list(request):
    products = product_queryset()
    query = request.GET.get('q', '').strip()[:100]
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(farmer__full_name__icontains=query))
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category__slug=category)
    condition = request.GET.get('condition', '')
    if condition in Product.Condition.values:
        products = products.filter(condition=condition)
    region = request.GET.get('region', '').strip()[:80]
    if region:
        products = products.filter(region__icontains=region)
    if request.GET.get('negotiable') == '1':
        products = products.filter(is_negotiable=True)
    for param, lookup in (('min_price', 'price_per_kg__gte'), ('max_price', 'price_per_kg__lte')):
        try:
            amount = Decimal(request.GET.get(param, ''))
            if amount >= 0:
                products = products.filter(**{lookup: amount})
        except (InvalidOperation, TypeError, ValueError):
            pass
    ordering = request.GET.get('sort')
    if ordering == 'price_asc':
        products = products.order_by('price_per_kg')
    elif ordering == 'price_desc':
        products = products.order_by('-price_per_kg')
    page = Paginator(products, 12).get_page(request.GET.get('page'))
    return render(request, 'catalog/product_list.html', {
        'page_obj': page,
        'products': page.object_list,
        'categories': Category.objects.all(),
        'filters': request.GET,
    })


def product_detail(request, slug):
    product = get_object_or_404(product_queryset(), slug=slug)
    related = product_queryset().filter(category=product.category).exclude(pk=product.pk)[:4]
    return render(request, 'catalog/product_detail.html', {'product': product, 'related_products': related})
