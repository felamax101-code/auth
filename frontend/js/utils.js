// ── API base ───────────────────────────────────────────────────────────────
const API = 'https://smartcomm.pythonanywhere.com/api/auth';

// ── Token helpers ──────────────────────────────────────────────────────────
const Auth = {
  setTokens(access, refresh) {
    localStorage.setItem('access', access);
    localStorage.setItem('refresh', refresh);
  },
  getAccess()  { return localStorage.getItem('access'); },
  getRefresh() { return localStorage.getItem('refresh'); },
  setResetToken(t) { sessionStorage.setItem('reset_token', t); },
  getResetToken()  { return sessionStorage.getItem('reset_token'); },
  clear() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    sessionStorage.removeItem('reset_token');
  },
  isLoggedIn() { return !!localStorage.getItem('access'); },
};

// ── HTTP helpers ───────────────────────────────────────────────────────────
async function apiFetch(endpoint, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (options.auth) {
    headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
  }
  const res = await fetch(`${API}${endpoint}`, {
    method:  options.method || 'GET',
    headers,
    body:    options.body ? JSON.stringify(options.body) : undefined,
  });
  let data;
  try { data = await res.json(); } catch { data = {}; }
  return { ok: res.ok, status: res.status, data };
}

// ── UI helpers ─────────────────────────────────────────────────────────────
function showAlert(el, message, type = 'error') {
  el.className = `alert alert-${type} show`;
  el.textContent = typeof message === 'object' ? JSON.stringify(message, null, 2) : message;
}

function hideAlert(el) {
  el.className = 'alert';
  el.textContent = '';
}

function showResponse(el, data) {
  el.classList.add('show');
  el.innerHTML = `<div class="label">Response</div>${JSON.stringify(data, null, 2)}`;
}

function setLoading(btn, loading) {
  btn.disabled = loading;
  btn.classList.toggle('loading', loading);
}

function flattenErrors(data) {
  if (typeof data === 'string') return data;
  if (Array.isArray(data)) return data.join(' ');
  if (typeof data === 'object') {
    return Object.entries(data)
      .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
      .join('\n');
  }
  return String(data);
}

// ── Nav active state ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const page = location.pathname.split('/').pop();
  document.querySelectorAll('nav a').forEach(a => {
    if (a.getAttribute('href') === page) a.classList.add('active');
  });
});
