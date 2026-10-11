from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('buyer/profile/', views.profile),
    path('farmer/', views.farmer_home, name='farmer'),
    path('farmer/products/', views.farmer_products, name='products'),
    path('farmer/products/add/', views.product_create, name='product_create'),
    path('farmer/products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('farmer/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('farmer/orders/', views.farmer_orders, name='orders'),
    path('farmer/orders/<int:pk>/advance/', views.advance_order, name='advance_order'),
]
