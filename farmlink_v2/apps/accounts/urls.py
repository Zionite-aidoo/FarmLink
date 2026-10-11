from django.shortcuts import redirect
from django.urls import path, reverse
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', lambda request: redirect(f"{reverse('accounts:login')}?mode=register"), name='register'),
    path('verify/', views.verify_view, name='verify'),
    path('resend/', views.resend_view, name='resend'),
    path('logout/', views.logout_view, name='logout'),
]

