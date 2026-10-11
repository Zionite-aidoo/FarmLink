from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('tracking/', views.tracking, name='tracking'),
    path('orders/', views.my_orders, name='list'),
    path('orders/<str:tracking_code>/', views.order_detail, name='detail'),
    path('order-success/<str:tracking_code>/', views.success, name='success'),
]
