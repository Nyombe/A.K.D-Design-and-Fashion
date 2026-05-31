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
    admin_link_map = {
        'users_changelist': (CustomUser, 'changelist'),
        'users_add': (CustomUser, 'add'),
        'products_changelist': (Product, 'changelist'),
        'products_add': (Product, 'add'),
        'orders_changelist': (Order, 'changelist'),
        'payments_changelist': (Payment, 'changelist'),
    }

    for key, (model, action) in admin_link_map.items():
        opts = model._meta
        try:
            dashboard_urls[key] = reverse(f'admin:{opts.app_label}_{opts.model_name}_{action}')
        except NoReverseMatch:
            dashboard_urls[key] = '#'

    try:
        dashboard_urls['analytics_dashboard'] = reverse('analytics:dashboard')
    except NoReverseMatch:
        dashboard_urls['analytics_dashboard'] = '#'

    extra_context.setdefault('dashboard_urls', dashboard_urls)
    return _original_index(request, extra_context)

admin.site.index = _custom_admin_index
admin.site.index_template = 'admin/jazzmin/dashboard.html'



