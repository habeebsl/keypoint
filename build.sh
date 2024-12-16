#!/bin/bash
# Build the project
echo "Building the project..."
pip3 install -r requirements.txt
python3 manage.py collectstatic --noinput