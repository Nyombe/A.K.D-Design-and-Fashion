#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Node.js via nodeenv..."
nodeenv -p --node=20.11.0

echo "Installing Node dependencies..."
npm install --include=dev

echo "Building Tailwind CSS..."
npm run build

if [ -f "./static/css/output.css" ]; then
    echo "Tailwind build successful: output.css generated."
else
    echo "ERROR: Tailwind build failed: output.css NOT found."
    # We don't exit here to allow collectstatic to run for other files, 
    # but the error message will be in the logs.
fi

echo "Cleaning previous static files..."
rm -rf ./staticfiles

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear --upload-unhashed-files

echo "Verifying static files..."
ls -R staticfiles/css || echo "staticfiles/css directory not found"

echo "Running database migrations..."
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set."
    echo "  → Go to your Render dashboard → your service → Environment"
    echo "  → Add DATABASE_URL with your Neon Postgres connection string."
    exit 1
fi
python manage.py migrate

echo "Creating admin superuser (if not exists)..."
python manage.py initadmin

echo "Migrating product images to Cloudinary (if configured)..."
if [ -n "$CLOUDINARY_CLOUD_NAME" ] && [ -n "$CLOUDINARY_API_KEY" ] && [ -n "$CLOUDINARY_API_SECRET" ]; then
    python manage.py migrate_images_to_cloudinary --old-host https://achol-fashion-store.onrender.com
    echo "Image migration complete."
else
    echo "Cloudinary not configured — skipping image migration."
fi

echo "Build finished successfully!"
exit 0
