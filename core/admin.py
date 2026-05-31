"""
Core app admin configuration.
"""
from django.contrib import admin

# Customize the default admin site
admin.site.site_header = "A.K.D FASHION AND DESIGN Management"
admin.site.site_title = "A.K.D Management"
admin.site.index_title = "Welcome to the A.K.D Admin Portal"
admin.site.index_template = 'admin/jazzmin/dashboard.html'

# Add dashboard context
_original_index = admin.site.index

def _dashboard_index(request, extra_context=None):
    from users.models import CustomUser
    from products.models import Product
    from orders.models import Order
    from payments.models import Payment

    extra_context = extra_context or {}
    
    try:
        extra_context.setdefault('dashboard_counts', {
            'users': {'count': CustomUser.objects.count()},
            'products': {'count': Product.objects.filter(is_active=True).count()},
            'orders': {'count': Order.objects.count()},
            'payments': {'count': Payment.objects.count()},
        })
    except Exception:
        extra_context.setdefault('dashboard_counts', {
            'users': {'count': 0},
            'products': {'count': 0},
            'orders': {'count': 0},
            'payments': {'count': 0},
        })

    return _original_index(request, extra_context)

admin.site.index = _dashboard_index



