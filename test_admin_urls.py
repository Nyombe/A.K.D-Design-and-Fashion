#!/usr/bin/env python
"""
Test admin URLs and reverse resolution
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

if __name__ == '__main__':
    # Test URL reversals
    print("=" * 60)
    print("TESTING ADMIN URL REVERSALS")
    print("=" * 60)

    urls_to_test = [
        'admin:users_customuser_changelist',
        'admin:products_product_changelist',
        'admin:orders_order_changelist',
        'admin:payments_payment_changelist',
        'analytics:dashboard',
    ]

    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"[OK] {url_name:40} -> {url}")
        except Exception as e:
            print(f"[FAIL] {url_name:40} -> ERROR: {e}")

    print("\n" + "=" * 60)
    print("TESTING ADMIN SITE REGISTRATION")
    print("=" * 60)

    from django.contrib import admin
    print(f"Admin site class: {admin.site.__class__.__name__}")
    print(f"Registered models: {len(admin.site._registry)}")
    for model, admin_instance in admin.site._registry.items():
        print(f"  [OK] {model._meta.app_label}.{model._meta.model_name}")
