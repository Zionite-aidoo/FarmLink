# FarmLink v2 — Architecture & Build Plan

**Goal:** Turn FarmLink from a v1 demo storefront into a complete, hostable marketplace web app where Ghanaian farmers list produce and buyers order it, with phone-number accounts, OTP login, order tracking, and a MoMo-ready payment layer.

**Locked decisions**
- Framework: **Django 6** (server-rendered templates, upgraded UI)
- Auth: **Phone number + OTP** (no passwords)
- Hosting target: **Render** (gunicorn + WhiteNoise + Postgres via `DATABASE_URL`, SQLite locally)

---

## 1. Project layout

```
farmlink_v2/
├── manage.py
├── requirements.txt
├── Procfile                  # web: gunicorn config.wsgi
├── build.sh                  # pip install → collectstatic → migrate → seed
├── runtime.txt
├── .env.example
├── config/                   # project package (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/             # phone User, OTP, profiles
│   ├── catalog/              # categories, products, images, search
│   ├── cart/                 # session cart (guest-friendly)
│   ├── orders/               # orders, items, status history, delivery zones
│   ├── payments/             # MoMo-ready payment abstraction (simulated in dev)
│   └── core/                 # home, about, contact, dashboard shell
├── templates/
├── static/
└── media/
```

## 2. Apps & data models

### accounts
- **User** (custom, `USERNAME_FIELD = "phone"`): phone (unique, E.164-ish `+233…`), full_name, role (`buyer` / `farmer` / `both`), region, city, is_phone_verified, date_joined.
- **OTPCode**: phone, code_hash (never store plain code), purpose (`login` / `register`), expires_at (5 min), attempts (max 5), consumed_at.
- SMS sending behind a provider interface: `ConsoleSMSBackend` (dev — prints OTP to server log), `HubtelSMSBackend` / `ArkeselSMSBackend` (live, env-configured). `SMS_BACKEND` env var switches.

### catalog
- **Category**: name, slug, icon (emoji), ordering.
- **Product**: farmer (FK → User), category, name, slug, description, price_per_kg, unit label, quantity_available, condition (fresh/good/ripe), is_negotiable, region, city, status (draft/active/paused), created_at.
- **ProductImage**: product FK, image, alt text, sort order (multiple photos per product — fixes v1's single image).
- Search & filters: name/description search, category, condition, region, price range, negotiable-only.

### cart
- Session-based cart (works for guests). On checkout the buyer authenticates via OTP.
- Stock is validated at add-to-cart **and** again at checkout.

### orders
- **DeliveryZone**: name, fee (GHS), estimated window (e.g. "24–48h"), is_active.
- **Order**: buyer FK, delivery address snapshot, phone, zone FK, subtotal, delivery_fee, total, status pipeline (pending → confirmed → preparing → out_for_delivery → delivered / cancelled), transaction_reference, created_at.
- **OrderItem**: order FK, product FK, farmer FK (denormalized for farmer dashboard), name/price snapshots, quantity_kg, subtotal. **Stock decremented atomically at order creation.**
- **OrderStatusHistory**: order FK, status, note, timestamp — powers the buyer's tracking timeline.
- Tracking is account-based (replaces v1's insecure phone-number lookup).

### payments
- **Payment**: order FK, method (`mtn_momo` / `vodafone_cash` / `airteltigo` / `cash_on_delivery`), amount, status (pending/paid/failed), provider_reference, raw_callback JSON.
- Provider abstraction: `payments/providers/base.py` → `SimulatedMoMoProvider` (dev, auto-approves like v1) and `MoMoProvider` stub for live keys. `PAYMENTS_MODE=simulated|live` env var.
- Cash-on-delivery supported; payment marked paid on delivery confirmation.

### core
- Home (hero, live stats from DB, featured produce, how-it-works, farmer CTA), About, Contact.
- Role-aware navbar: Browse / Cart / Login → after login: My Orders, Farmer Dashboard (if farmer), Logout.

## 3. Screens

| Area | Pages |
|---|---|
| Public | Home, Catalog (search/filter), Product detail (gallery), About, Contact |
| Auth | Login (phone → OTP), Register (phone + name + role → OTP) |
| Buyer | Cart, Checkout (address + zone + payment method), Order success, My Orders, Order tracking timeline, Profile |
| Farmer | Dashboard (earnings, stock, incoming orders), Product CRUD (multi-image), Order management (advance status) |
| Admin | Django admin over all models |

## 4. Security & production hardening

- OTP codes hashed, expiring, rate-limited; login throttling.
- CSRF everywhere; `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` from env (as v1).
- `DEBUG=False` default; secret key from env only.
- Atomic stock deduction (`select_for_update` / `F()` expressions) to prevent overselling.
- Farmers can only edit their own products/orders (object-level permission checks).

## 5. Build phases

1. ✅ Architecture plan (this document)
2. ✅ Scaffold project + settings + apps skeleton
3. ✅ accounts: custom User, OTP request/verify, console SMS backend
4. ✅ catalog: models, admin, public catalog pages, farmer product CRUD
5. ✅ cart + checkout + orders + delivery zones + tracking timeline
6. ✅ payments: simulated MoMo flow + provider abstraction
7. ✅ dashboards (buyer + farmer), order status management
8. ✅ UI polish (new design system), seed data (Ghanaian categories + farmers + produce + images)
9. ✅ Deployment files (Procfile, build.sh, .env.example), test suite (22 unit & integration tests), README, final verification

## 6. What carries over from v1

- The Order status pipeline concept (kept, now with history).
- Simulated-payment fallback for development.
- Render deployment pattern (WhiteNoise, `DATABASE_URL` parsing, `RENDER_EXTERNAL_URL`).
- Ghanaian produce seed data concept (expanded with categories & images).
- Brand content: contact details, social links, "Fresh from farm to table".
