web: python manage.py migrate --noinput && gunicorn myproject.wsgi:application --bind 0.0.0.0:${PORT:-8000} --access-logfile - --error-logfile -
