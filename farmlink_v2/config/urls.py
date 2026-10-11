from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'FarmLink operations'
admin.site.site_title = 'FarmLink admin'
admin.site.index_title = 'Marketplace management'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('products/', include('apps.catalog.urls')),
    path('cart/', include('apps.cart.urls')),
    path('', include('apps.orders.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
