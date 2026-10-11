from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'category', 'price_per_kg', 'quantity_available', 'status', 'is_approved')
    list_filter = ('status', 'is_approved', 'category', 'condition', 'region')
    search_fields = ('name', 'farmer__phone', 'farmer__full_name', 'city', 'region')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_approved',)
    inlines = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'ordering')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt', 'ordering')
