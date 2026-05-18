"""
Production settings for ecommerce project.
"""

from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='.onrender.com,akd-fashion-design.onrender.com,akd.com,www.akd.com', cast=Csv())

# Add CSRF trusted origins for Render
CSRF_TRUSTED_ORIGINS = [
    'https://akd-fashion-design.onrender.com',
    'https://akd.com',
    'https://www.akd.com',
    'https://*.onrender.com',
]

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=''),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
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
    "https://akd-fashion-design.onrender.com",
]
