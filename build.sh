#!/bin/bash

echo "Starting custom build script"

# Run database migrations (if applicable)
python manage.py migrate

# Collect static files (if Django is used)
python manage.py collectstatic --noinput

echo "Build script completed successfully"
