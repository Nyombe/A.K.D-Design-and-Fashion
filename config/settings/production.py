"""
Production settings for ecommerce project.
"""

from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='achol-fashion-store.onrender.com', cast=Csv())

# Automatically trust Render's dynamic hostname if available
RENDER_EXTERNAL_HOSTNAME = config('RENDER_EXTERNAL_HOSTNAME', default='')
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Add CSRF trusted origins for Render
CSRF_TRUSTED_ORIGINS = [
    'https://achol-fashion-store.onrender.com',
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

import sys

_database_url = config('DATABASE_URL', default='')
if not _database_url:
    # During build phase (e.g. collectstatic), use a dummy in-memory database to allow assets build.
    if 'collectstatic' in sys.argv:
        _database_url = 'sqlite:///:memory:'
    else:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            "DATABASE_URL environment variable is not set. "
            "Add your Neon Postgres connection string in the Render dashboard under "
            "Environment → Environment Variables."
        )

# Use parse() instead of config() — dj-database-url 2.x removed ssl_require from
# config(), causing it to silently return {} on failure. parse() raises ValueError
# on a bad URL. SSL is handled by ?sslmode=require already in the Neon URL.
DATABASES = {
    'default': dj_database_url.parse(
        _database_url,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# HTTPS & Security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year

# Static files - Simplified WhiteNoise for stability
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Use the non-manifest storage to avoid crashes on missing file references
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False

# Media files - Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://achol-fashion-store.onrender.com",
]
if RENDER_EXTERNAL_HOSTNAME:
    CORS_ALLOWED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')
