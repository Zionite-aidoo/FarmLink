from django.urls import path
from apps.catalog.views import home
from . import views

app_name = 'core'
urlpatterns = [
    path('', home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
