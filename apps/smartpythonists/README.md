# SmartPythonists Frontend v3.0

Production-ready frontend for the SmartPythonists DRF learning platform.

## Files

| File | Description |
|------|-------------|
| `sp_core.js` | Shared engine — API client, auth, notifications, suggestions, ads, toast |
| `auth.html` | Sign in / Register / Forgot password / Email verification / Password reset |
| `home.html` | Post listing — filters, search, featured, suggestions, ads, trending |
| `post.html` | Post detail — markdown, TOC, comments, replies, likes, suggestions, ads |
| `dashboard.html` | User dashboard — overview, skills radar, heatmap, notifications, settings |
| `resources.html` | Learning resources — filter by topic/type/difficulty/price, suggestions |

## Setup

1. Place all files in your Django `static/` or serve from any web server
2. Ensure `sp_core.js` is in the same directory as the HTML files
3. Your Django project must have these URL mounts:
   - `/api/auth/` → users app
   - `/api/smartpythonists/` → smartpythonists app
4. CORS must allow your frontend origin in Django settings

## Google Ads Integration

In `sp_core.js`, find `ca-pub-REPLACE_YOUR_PUB_ID` and `REPLACE_YOUR_AD_SLOT` — replace with your AdSense publisher ID and slot ID. Internal ads from your database will show first; Google Ads renders as fallback when no active internal ads exist for a given topic.

## Features

- **JWT Auth** — silent token refresh, 401 auto-redirect
- **Real-time Notifications** — polls every 30s, bell dropdown, unread badge
- **Suggestion Engine** — tracks reading history in localStorage, surfaces personalised posts/resources
- **Contextual Ads** — serves internal ads by topic/difficulty, falls back to Google AdSense slot
- **Email Verification** — handles `?verify=TOKEN` URL from email link
- **Password Reset** — handles `?reset=TOKEN` URL from email link
- **Threaded Comments** — create, reply, like/unlike, delete
- **Markdown Rendering** — via marked.js with syntax highlighting
- **Reading Progress Bar** — scroll-based on post detail
- **Activity Heatmap** — GitHub-style 6-month grid
- **Skill Radar Chart** — pure Canvas, 10 DRF topics
- **⌘K Search** — global keyboard shortcut

## Deployment

For production, set the API base URLs in `sp_core.js`:
```js
const AUTH = '/api/auth';      // or 'https://api.yourdomain.com/api/auth'
const APP  = '/api/smartpythonists';
```
