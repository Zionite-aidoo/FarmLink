# FarmLink v2

FarmLink v2 is a separate Django marketplace project based on the team's [v2 specification](../FARMLINK_V2_PLAN.md) and the supplied PDF. It leaves the v1 project at the repository root unchanged.

## Current features

- Phone number sign-in and registration using expiring, hashed six-digit OTPs. Local development prints OTPs to the server console.
- Farmer and buyer roles, profile editing, and staff-managed moderation.
- Produce catalog with category, condition, region, price, search, and negotiable filters; product photo galleries; farmer-owned listing management.
- Guest session cart and authenticated checkout, delivery zones, order snapshots, atomic stock decrement, tracking code plus phone lookup, and order status history.
- Simulated Mobile Money for local development only, plus cash on delivery. Live payment and SMS providers are not connected yet.
- Buyer order view, farmer dashboard and order management, contact form, and Django admin.
- Render deployment files, WhiteNoise static files, SQLite locally, and Postgres through `DATABASE_URL`.

## Run locally on Windows

From this folder, use Python 3.12 or newer:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Generate a local Django key and put it in `DJANGO_SECRET_KEY` in `.env`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Then initialize the local database and start the site:

```powershell
python manage.py migrate
python manage.py seed_initial_data
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Sign in and registration codes appear in the same console where `runserver` is running. For the first staff account, use an international phone number such as `+233241234567` with `createsuperuser`. Staff can review new produce at `/admin/`; listings stay hidden from buyers until approved. The development simulated MoMo option never contacts a payment network.

## Configuration

See `.env.example`. Production requires a strong `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and a Postgres `DATABASE_URL`. Live SMS and Mobile Money remain provider integration work; do not set the local console SMS backend in production. Set `SECURE_SSL_REDIRECT=True` behind HTTPS.

For Render, use this folder as the service root. `build.sh` installs dependencies, collects static files, migrates the database, and creates starter categories and delivery zones. Create the first staff user through a controlled management command or Django shell; no admin account is seeded by the build.

## Current boundaries

This is the initial usable v2 foundation, not the full production roadmap. Saved buyer addresses, notifications, payment webhooks, live Hubtel/mNotify/Africa's Talking SMS adapters, live MTN/Hubtel payments, and broader operational workflows still need implementation. Review the plan and continue the remaining work in small, reviewable increments.
