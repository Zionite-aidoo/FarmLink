web: python manage.py collectstatic --noinput && gunicorn farm_link.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3


