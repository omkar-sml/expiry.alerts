# EXPIRY.ALERT — Medicine and Food Expiry Tracker

Smart Household Expiry Management System — **Food + Medicine**.
Helps households prevent unsafe use and reduce waste with automatic expiry tracking.

Built with **Python + Django + SQLite + HTML/CSS/Bootstrap** — beginner-friendly.

### Features
- **Auth:** Register, Login, Logout (Django built-in auth)
- **Dashboard:** Total medicines, Total food items, Expiring soon (≤7 days, Orange), Expired (Red), Safe (Green) + critical list
- **Medicine CRUD:** Add / View / Edit / Delete — fields: Name, Quantity, Expiry Date — user-isolated
- **Food CRUD:** Add / View / Edit / Delete — fields: Name, Quantity, Expiry Date — user-isolated
- **Expiry Status (auto):** `Safe` (>7 days, Green), `Expiring Soon` (0–7 days, Orange), `Expired` (<0 days, Red)

### Models
- `User` (Django `auth.User`)
- `Medicine` → `user` FK, `name`, `quantity`, `expiry_date`
- `FoodItem` → `user` FK, `name`, `quantity`, `expiry_date`

### Pages
- `/` Home, `/register/`, `/login/`, `/logout/`
- `/dashboard/` Dashboard
- `/medicines/` , `/medicines/add/` , `/medicines/edit/<id>/` , `/medicines/delete/<id>/`
- `/foods/` , `/foods/add/` , `/foods/edit/<id>/` , `/foods/add/` , `/foods/delete/<id>/`

### Quick Start

```bash
# 1) Go to project folder
cd "yash prject"   # folder name as created
# If using Terminal, quote the space: cd "yash prject"  or cd yash\ prject

# 2) (optional) create venv
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# 3) Install
pip install -r requirements.txt

# 4) Migrate
python manage.py migrate

# 5) (optional) create admin
python manage.py createsuperuser

# 6) Run
python manage.py runserver
# open http://127.0.0.1:8000/
```

### Test the flow
1. Register → auto-login → Dashboard (0 counts)
2. Add Medicine: `Paracetamol`, qty `10`, expiry `2026-09-10` → shows Orange (Expiring Soon)
3. Add Food: `Milk`, qty `1`, expiry `2026-09-20` → Green (Safe); add `Bread`, expiry `2026-09-01` → Red (Expired)
4. Use filters on Medicines/Foods pages: All / Safe / Expiring Soon / Expired
5. Edit/Delete works and is user-isolated (you only see your own items)

### Project Structure
```
yash prject/
  manage.py
  config/          # project settings (settings.py, urls.py)
  tracker/         # app (models.py, views.py, forms.py, admin.py, urls.py)
  templates/       # base.html, home.html, dashboard.html, registration/*, tracker/*
  static/css/      # style.css
  db.sqlite3       # created after migrate (SQLite)
  requirements.txt
  README.md
```

### Customizing Threshold
Expiry logic is in `tracker/models.py` (`status` property, 7-day window). Change `days <= 7` to adjust.

### Notes
- Bootstrap 5 + Icons via CDN (no npm needed)
- Responsive, clean cards, color-coded badges
- All CRUD is login-required (`@login_required`)
- No extra dependencies beyond Django

### Author
Yash Project — Sep 2026 — EXPIRY.ALERT v1.0

---

## Email Notifications (New)

**How it works:**
- In-app: bell + banner + `/notifications/` auto-created (≤7 days Orange, Expired Red)
- Email: also sent when a product becomes expiring/expired
  - **Single alert:** on add/edit if status is Expiring Soon/Expired (via `tracker/signals.py`)
  - **Daily digest:** via `python manage.py check_expiry` (summary for all users)

**Default (beginner-friendly):**
- `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` in `config/settings.py`
- Emails print to terminal where `runserver` is running — no setup needed. Verified above.

**For real email (Gmail example):**
```bash
# set env vars before runserver
export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER=your@gmail.com
export EMAIL_HOST_PASSWORD=your_app_password  # Gmail > App Passwords
export DEFAULT_FROM_EMAIL="EXPIRY.ALERT <your@gmail.com>"

python manage.py runserver
# or daily cron:
python manage.py check_expiry          # sends digest
python manage.py check_expiry --dry-run # preview
python manage.py check_expiry --user yash
```

**Test it:**
- Ensure user has email (admin or shell: `User.objects.filter(username='yash').update(email='you@gmail.com')`)
- Add medicine with expiry in 2 days → console shows email immediately
- Visit `/email-preview/` → see HTML preview + button "Send test email"
- Run `python manage.py check_expiry` → sends summary to all users with critical items

**Cron (daily 8am):**
```
0 8 * * * cd "/Users/sml.cloud/Downloads/yash prject" && python manage.py check_expiry >> /tmp/expiry_cron.log 2>&1
```

