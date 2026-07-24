#!/usr/bin/env bash

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate

# Seed the database with sample products & admin user
python manage.py seed_data
