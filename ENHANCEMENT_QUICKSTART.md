# 🚀 Quick Start Guide - A.K.D Fashion Enhancements

> Get the luxury fashion e-commerce enhancements running in 15 minutes

## Prerequisites
- Python 3.8+
- Django 4.2
- Virtual environment activated
- Existing A.K.D project

---

## 5-Minute Setup

### 1️⃣ Apply Model Changes
```bash
cd /path/to/akd

# The models are already updated in the files above
# Just generate and apply migrations

python manage.py makemigrations products orders
python manage.py migrate
```

### 2️⃣ Update URLs
```python
# config/urls.py - Add these imports and routes

from django.urls import path, include
from orders.views_v2 import CartViewSet, GuestCheckoutView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'carts', CartViewSet, basename='cart')

urlpatterns = [
    # ... existing patterns ...
    
    # NEW ENDPOINTS
    path('api/v2/', include(router.urls)),  # /api/v2/carts/
    path('api/v2/checkout/guest/', GuestCheckoutView.as_view(), name='guest_checkout'),
]
```

### 3️⃣ Include Cart Drawer in Base Template
```html
<!-- templates/base/base.html - Add before closing </body> -->

{% include 'cart_drawer.html' %}

<!-- Add this button to your header/navbar -->
<button onclick="openCartDrawer()" class="relative p-2 hover:bg-gray-100 rounded-lg transition">
    <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
    </svg>
    <span class="cart-count hidden absolute -top-2 -right-2 bg-red-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center text-center">0</span>
</button>
```

### 4️⃣ Test in Django Admin
```bash
python manage.py runserver

# Go to http://localhost:8000/admin/
# You should see new models:
#   - Product Variant Attributes
#   - Product Variant Options
#   - Product Variant Values
#   - Product Recommendations
```

---

## Creating Variant Data (Admin Interface)

### Via Django Admin
```
1. Go to /admin/products/productvariantattribute/
2. Click "Add Product Variant Attribute"
3. Create one for each type:
   - Name: size → Display: Size
   - Name: color → Display: Color
   - Name: material → Display: Material

4. Then go to /admin/products/productvariantoption/
5. Add options for Size:
   - Value: "Small", Display: "S"
   - Value: "Medium", Display: "M"
   - Value: "Large", Display: "L"

6. Then go to /admin/products/productvari antvalue/
7. For each product, add variants:
   - Product: "Blue Dress"
   - SKU: "DRESS-BLUE-M"
   - Attributes: {"size": "Medium", "color": "Blue"}
   - Stock: 20
   - Price override: (leave blank to use product price)
```

### Via Python Shell
```bash
python manage.py shell

from products.models import Product, ProductVariantAttribute, ProductVariantOption, ProductVariantValue

# Create attributes
size_attr, _ = ProductVariantAttribute.objects.get_or_create(
    name='size',
    defaults={'display_name': 'Size'}
)

# Create options
small_opt, _ = ProductVariantOption.objects.get_or_create(
    attribute=size_attr,
    value='Small',
    defaults={'display_value': 'S', 'order': 1}
)

# Create variant value
product = Product.objects.get(id=1)
variant = ProductVariantValue.objects.create(
    product=product,
    sku='DRESS-BLUE-M-SILK',
    attributes={'size': 'Medium', 'color': 'Blue', 'material': 'Silk'},
    stock=15
)
```

---

## Testing the Features

### 1. Test Cart Drawer
```html
<!-- Add to any template and test -->
<button onclick="openCartDrawer()">Open Cart</button>

<!-- Should work:
  - Drawer slides in from right
  - Add item button works
  - Quantity controls work
  - Close button works
-->
```

### 2. Test Add to Cart (with variants)
```javascript
// In browser console
const cart = {
    productId: 1,
    productName: "Blue Dress",
    productImage: "https://...",
    price: "99.99",
    quantity: 1,
    variant_selections: {size: "M", color: "Blue"},
    variantInfo: "Size: M, Color: Blue",
    stock: 20
};

let stored = JSON.parse(localStorage.getItem('cart') || '{"items":[]}');
stored.items.push(cart);
localStorage.setItem('cart', JSON.stringify(stored));

// Refresh page - item should still be there!
```

### 3. Test API Endpoint
```bash
# Add to cart via API
curl -X POST http://localhost:8000/api/v2/carts/add_item/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2,
    "variant_selections": {"size": "M"}
  }'

# Should return 201 Created with cart item data
```

---

## Using Enhanced Templates

### New Product Detail Page
```html
<!-- Update products/product_detail.html to use: -->
{% extends 'base/base.html' %}
{% load static %}

<!-- Content from templates/product_detail_enhanced.html -->
```

### New Luxury Homepage
```python
# products/urls.py
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home_luxury_bento.html'), name='home'),
]
```

---

## Key JavaScript Functions

```javascript
// Open/close cart drawer
openCartDrawer()
closeCartDrawer()

// Add item
addToCart(productId, quantity, variantSelections)

// Update quantity
updateCartQuantity(cartItemId, newQuantity)

// Remove item
removeFromCart(cartItemId)

// Get current cart
const cart = JSON.parse(localStorage.getItem('cart'))

// Update cart count badge
updateCartCount()
```

---

## Deployment Checklist

- [ ] Migrations applied to production
- [ ] Admin models visible
- [ ] Variant data created for products
- [ ] Cart drawer included in base template
- [ ] New API endpoints registered in urls.py
- [ ] JSON-LD schema visible in page source
- [ ] Cart drawer works on mobile
- [ ] Guest checkout works

---

**🎉 Ready to deploy!** See `IMPLEMENTATION_GUIDE.md` for complete documentation.

