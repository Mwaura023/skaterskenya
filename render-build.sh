#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies (already handled by Render with requirements.txt)

# Run migrations
python manage.py migrate

# (Optional but recommended) collect static files
python manage.py collectstatic --noinput
