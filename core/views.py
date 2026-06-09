from django.views.generic import TemplateView
from django.shortcuts import render
from products.models import Category, Product


class HomePageView(TemplateView):
    """Homepage view."""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            is_active=True
        ).select_related('category')[:12]
        context['categories'] = Category.objects.filter(is_active=True)[:6]
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'

class ContactView(TemplateView):
    template_name = 'core/contact.html'


import os
from django.views.static import serve
from django.http import HttpResponseRedirect

def serve_media_with_fallback(request, path, document_root=None, show_indexes=False):
    try:
        if document_root:
            fullpath = os.path.join(document_root, path)
            if os.path.exists(fullpath) and os.path.isfile(fullpath):
                return serve(request, path, document_root, show_indexes)
    except Exception:
        pass
    
    path_lower = path.lower()
    
    # 1. Shoes / Footwear / Boots
    if any(keyword in path_lower for keyword in ['shoe', 'boot', 'footwear', 'sh', 'leather', 'run', 'sneaker', 'heel']):
        placeholder_url = "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600&auto=format&fit=crop"
    # 2. Pants / Trousers / Joggers / Clothing
    elif any(keyword in path_lower for keyword in ['pant', 'trouser', 'jogger', 'wear', 'suit', 'cloth', 'jeans', 'shirt', 'jacket']):
        placeholder_url = "https://images.unsplash.com/photo-1479064555552-3ef4979f8908?q=80&w=600&auto=format&fit=crop"
    # 3. Default Premium Fashion collection
    else:
        placeholder_url = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?q=80&w=600&auto=format&fit=crop"
        
    return HttpResponseRedirect(placeholder_url)
