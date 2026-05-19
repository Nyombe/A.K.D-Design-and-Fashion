"""
URL configuration for ecommerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from products.sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap

from django_otp.admin import OTPAdminSite
from django_otp.forms import OTPAuthenticationForm
from django_otp import devices_for_user

class FlexOTPAuthenticationForm(OTPAuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_active:
            has_confirmed_device = False
            for device in devices_for_user(user):
                if device.confirmed:
                    has_confirmed_device = True
                    break
            
            if not has_confirmed_device:
                from django.contrib.auth.forms import AuthenticationForm
                return super(OTPAuthenticationForm, self).clean()
                
        return super().clean()

class FlexOTPAdminSite(OTPAdminSite):
    login_form = FlexOTPAuthenticationForm

admin.site.__class__ = FlexOTPAdminSite

sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('management/analytics/', include('analytics.urls')),
    path('management/', admin.site.urls),
    path('api/auth/', include('users.urls.api')),
    path('api/products/', include('products.urls.api')),
    path('api/orders/', include('orders.urls.api')),
    path('api/payments/', include('payments.urls')),
    path('auth/', include('users.urls.web')),
    path('products/', include('products.urls.web')),
    path('cart/', include('orders.urls.cart')),
    path('orders/', include('orders.urls.web')),
    
    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
