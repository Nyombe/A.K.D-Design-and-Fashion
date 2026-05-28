"""
Core app admin configuration.
"""
from django.contrib import admin
from django.urls import NoReverseMatch, reverse

# Customize the default admin site
admin.site.site_header = "A.K.D FASHION AND DESIGN Management"
admin.site.site_title = "A.K.D Management"
admin.site.index_title = "Welcome to the A.K.D Admin Portal"

# Dashboard overview counts
_original_index = admin.site.index

def _custom_admin_index(request, extra_context=None):
    from users.models import CustomUser
    from products.models import Product
    from orders.models import Order
    from payments.models import Payment

    extra_context = extra_context or {}
    extra_context.setdefault('dashboard_counts', {
        'users': {'count': CustomUser.objects.count()},
        'products': {'count': Product.objects.filter(is_active=True).count()},
        'orders': {'count': Order.objects.count()},
        'payments': {'count': Payment.objects.count()},
    })

    dashboard_urls = {}
    mapping = {
        'users_changelist': 'admin:users_customuser_changelist',
        'users_add': 'admin:users_customuser_add',
        'products_changelist': 'admin:products_product_changelist',
        'products_add': 'admin:products_product_add',
        'orders_changelist': 'admin:orders_order_changelist',
        'payments_changelist': 'admin:payments_payment_changelist',
        'analytics_dashboard': 'analytics:dashboard',
    }
    for key, name in mapping.items():
        try:
            dashboard_urls[key] = reverse(name)
        except NoReverseMatch:
            dashboard_urls[key] = '#'

    extra_context.setdefault('dashboard_urls', dashboard_urls)
    return _original_index(request, extra_context)

admin.site.index = _custom_admin_index
admin.site.index_template = 'admin/jazzmin/dashboard.html'



