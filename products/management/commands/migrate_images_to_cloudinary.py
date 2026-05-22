"""
Management command to migrate existing product images to Cloudinary.

Usage:
    python manage.py migrate_images_to_cloudinary
    python manage.py migrate_images_to_cloudinary --old-host https://achol-fashion-store.onrender.com
    python manage.py migrate_images_to_cloudinary --dry-run
"""

import io
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from products.models import ProductImage


class Command(BaseCommand):
    help = 'Migrate existing product images from old server to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--old-host',
            type=str,
            default='https://achol-fashion-store.onrender.com',
            help='Base URL of the old Render server where images are hosted',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would happen without making changes',
        )

    def handle(self, *args, **options):
        old_host = options['old_host'].rstrip('/')
        dry_run = options['dry_run']

        images = ProductImage.objects.filter(image__isnull=False).exclude(image='')
        total = images.count()

        if total == 0:
            self.stdout.write(self.style.WARNING('No product images with file references found.'))
            return

        self.stdout.write(self.style.NOTICE(f'Found {total} image(s) to migrate from {old_host}'))

        success = 0
        failed = 0

        for img in images:
            image_name = str(img.image)  # e.g. "products/shoe.jpg"
            old_url = f'{old_host}/media/{image_name}'
            product_name = img.product.name

            self.stdout.write(f'  → [{product_name}] Fetching: {old_url}')

            if dry_run:
                self.stdout.write(self.style.WARNING('    [DRY RUN] Would download and re-upload to Cloudinary.'))
                continue

            try:
                response = requests.get(old_url, timeout=30)
                if response.status_code == 200:
                    # Get the filename only
                    filename = image_name.split('/')[-1]
                    content = ContentFile(response.content, name=filename)

                    # Save back — Django will now use Cloudinary storage backend
                    img.image.save(filename, content, save=True)
                    success += 1
                    self.stdout.write(self.style.SUCCESS(f'    ✓ Uploaded to Cloudinary: {filename}'))
                else:
                    self.stdout.write(
                        self.style.ERROR(f'    ✗ HTTP {response.status_code} — Could not fetch image.')
                    )
                    # Fall back: save the old URL so the image still displays
                    if not img.image_url:
                        img.image_url = old_url
                        img.save(update_fields=['image_url'])
                        self.stdout.write(self.style.WARNING(f'    → Saved old URL as fallback: {old_url}'))
                    failed += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    ✗ Error: {e}'))
                # Fall back: save the old URL so the image still displays
                if not img.image_url:
                    img.image_url = old_url
                    img.save(update_fields=['image_url'])
                    self.stdout.write(self.style.WARNING(f'    → Saved old URL as fallback: {old_url}'))
                failed += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✓ Done! Migrated: {success} | Failed: {failed} | Total: {total}'))
        if failed > 0:
            self.stdout.write(self.style.WARNING(
                'Images that failed to migrate were saved with the old server URL as a fallback.'
            ))
