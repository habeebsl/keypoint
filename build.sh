#!/bin/bash

echo "Starting custom build script"

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if applicable)
python manage.py migrate

# Collect static files (if Django is used)
python manage.py collectstatic --noinput

echo "Build script completed successfully"
