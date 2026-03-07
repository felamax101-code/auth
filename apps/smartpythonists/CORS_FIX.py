# ══════════════════════════════════════════════════════
#  SmartPythonists — CORS Fix (VS Code Live Server setup)
# ══════════════════════════════════════════════════════

# ── STEP 1: Install corsheaders ────────────────────────
# Run this in your terminal (same folder as manage.py):

    pip install django-cors-headers


# ── STEP 2: Patch settings.py ──────────────────────────
# Open your settings.py and make these 3 changes:

# --- 2a: Add to INSTALLED_APPS ---
INSTALLED_APPS = [
    # ...your existing apps...
    'corsheaders',         # ← ADD THIS
]

# --- 2b: Add to MIDDLEWARE (MUST be the very first item) ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',    # ← ADD THIS FIRST
    'django.middleware.security.SecurityMiddleware',
    # ...rest of your middleware unchanged...
]

# --- 2c: Add these lines anywhere in settings.py ---
CORS_ALLOW_ALL_ORIGINS = True          # allows Live Server port 5500
CORS_ALLOW_CREDENTIALS = True          # allows Authorization header
CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'origin',
    'x-requested-with',
]


# ── STEP 3: Restart Django ─────────────────────────────
# Stop your server (Ctrl+C) then restart:

    python manage.py runserver


# ── STEP 4: Update sp_core.js ──────────────────────────
# In sp_core.js, the top two lines should now read:
# (already done in the downloaded zip)

    const AUTH = 'http://127.0.0.1:8000/api/auth';
    const APP  = 'http://127.0.0.1:8000/api/smartpythonists';


# ── THAT'S IT ──────────────────────────────────────────
# Open auth.html with Live Server → login should work.
#
# The "Broken pipe" error in Django terminal = harmless,
# just means the browser closed the tab. Ignore it.
#
# ── FOR PRODUCTION (when you deploy) ──────────────────
# Replace CORS_ALLOW_ALL_ORIGINS = True with:
#
# CORS_ALLOWED_ORIGINS = [
#     "https://yourdomain.com",
# ]
# And change sp_core.js URLs back to:
#     const AUTH = '/api/auth';
#     const APP  = '/api/smartpythonists';
