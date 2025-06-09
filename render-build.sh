#!/usr/bin/env bash
# render-build.sh

# Exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Collect static files
python manage.py collectstatic --no-input
