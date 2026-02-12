from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Apps - SOLO UNA VEZ cada app
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('dashboard/', include('apps.users.urls')),  # Solo esta línea para users
    path('accounts/', include('django.contrib.auth.urls')),  # Para login/logout de Django
    
    # Otras apps (cada una una sola vez)
    path('products/', include('apps.products.urls')),
    path('warehouses/', include('apps.warehouses.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('movements/', include('apps.movements.urls')),
    path('audit/', include('apps.audit.urls')),
    path('reports/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]