#!/bin/bash
# Build the project
echo "Building the project..."
mkdir -p /var/task/staticfiles
pip install -r requirements.txt
python manage.py collectstatic --noinput