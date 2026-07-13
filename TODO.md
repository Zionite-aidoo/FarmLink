# FarmLink - Render Deployment Checklist

- [x] Inspect current Django project structure and dependencies
- [ ] Edit `farm_link/settings.py` for production (DEBUG=False, ALLOWED_HOSTS, Postgres via DATABASE_URL, STATIC_ROOT, whitenoise config)
- [ ] Add production start command (gunicorn) and ensure it runs from Render
- [ ] Create Render Postgres instance (free tier) and attach to Web Service
- [ ] Configure Render Web Service build/start commands + env vars
- [ ] Run `python manage.py migrate` and `collectstatic` during Render deploy
- [ ] Smoke test deployed URL
- [ ] (Optional) Set up media storage for uploaded product images

