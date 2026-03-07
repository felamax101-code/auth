// ============================================================
// SmartPythonists — Core API Client & Utilities
// ============================================================

const API_BASE = 'http://127.0.0.1:8000'; // change to your server
const AUTH_BASE = `${API_BASE}/api/auth`;
const SP_BASE   = `${API_BASE}/api/smartpythonists`;

// ─── Token Management ────────────────────────────────────────
const Auth = {
  getAccess  : () => localStorage.getItem('sp_access'),
  getRefresh : () => localStorage.getItem('sp_refresh'),
  getUser    : () => JSON.parse(localStorage.getItem('sp_user') || 'null'),
  isLoggedIn : () => !!localStorage.getItem('sp_access'),
  isStaff    : () => { const u = Auth.getUser(); return u && u.is_staff; },

  save(data) {
    localStorage.setItem('sp_access',  data.access);
    localStorage.setItem('sp_refresh', data.refresh);
    localStorage.setItem('sp_user',    JSON.stringify(data.user));
  },

  clear() {
    ['sp_access','sp_refresh','sp_user'].forEach(k => localStorage.removeItem(k));
  },

  async refresh() {
    const token = Auth.getRefresh();
    if (!token) return false;
    try {
      const res = await fetch(`${AUTH_BASE}/token/refresh/`, {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ refresh: token })
      });
      if (!res.ok) { Auth.clear(); return false; }
      const data = await res.json();
      localStorage.setItem('sp_access', data.access);
      return true;
    } catch { Auth.clear(); return false; }
  }
};

// ─── HTTP Client ─────────────────────────────────────────────
async function http(url, options = {}, retry = true) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (Auth.isLoggedIn()) headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
  const res = await fetch(url, { ...options, headers });

  if (res.status === 401 && retry) {
    const ok = await Auth.refresh();
    if (ok) return http(url, options, false);
    Auth.clear();
    window.location.href = 'auth.html';
    return;
  }
  return res;
}

async function api(url, options = {}) {
  const res = await http(url, options);
  if (!res) return { ok: false, data: null };
  let data;
  try { data = await res.json(); } catch { data = null; }
  return { ok: res.ok, status: res.status, data };
}

// ─── API Namespaces ───────────────────────────────────────────
const UserAPI = {
  register : d => api(`${AUTH_BASE}/register/`,             { method:'POST', body:JSON.stringify(d) }),
  verifyOTP: d => api(`${AUTH_BASE}/email/verify/`,         { method:'POST', body:JSON.stringify(d) }),
  resendOTP: d => api(`${AUTH_BASE}/email/verify/resend/`,  { method:'POST', body:JSON.stringify(d) }),
  login    : d => api(`${AUTH_BASE}/login/`,                { method:'POST', body:JSON.stringify(d) }),
  logout   : d => api(`${AUTH_BASE}/logout/`,               { method:'POST', body:JSON.stringify(d) }),
  profile  : () => api(`${AUTH_BASE}/profile/`),
  updateProfile: d => api(`${AUTH_BASE}/profile/`,          { method:'PUT',  body:JSON.stringify(d) }),
  resetRequest : d => api(`${AUTH_BASE}/password/reset/`,   { method:'POST', body:JSON.stringify(d) }),
  resetConfirm : d => api(`${AUTH_BASE}/password/reset/confirm/`, { method:'POST', body:JSON.stringify(d) }),
  changePassword: d => api(`${AUTH_BASE}/password/change/`, { method:'POST', body:JSON.stringify(d) }),
  deleteAccount: d => api(`${AUTH_BASE}/account/delete/`,   { method:'DELETE', body:JSON.stringify(d) }),
  reactivate: d => api(`${AUTH_BASE}/account/reactivate/`,  { method:'POST', body:JSON.stringify(d) }),
};

const PostAPI = {
  list   : (p={}) => api(`${SP_BASE}/posts/?${new URLSearchParams(p)}`),
  detail : id  => api(`${SP_BASE}/posts/${id}/`),
  featured: () => api(`${SP_BASE}/posts/featured/`),
  create : d   => api(`${SP_BASE}/posts/`,    { method:'POST',   body:JSON.stringify(d) }),
  update : (id,d)=> api(`${SP_BASE}/posts/${id}/`, { method:'PUT', body:JSON.stringify(d) }),
  delete : id  => api(`${SP_BASE}/posts/${id}/`, { method:'DELETE' }),
};

const CommentAPI = {
  list  : pid      => api(`${SP_BASE}/posts/${pid}/comments/`),
  create: (pid,d)  => api(`${SP_BASE}/posts/${pid}/comments/`, { method:'POST', body:JSON.stringify(d) }),
  update: (pid,cid,d)=> api(`${SP_BASE}/posts/${pid}/comments/${cid}/`, { method:'PUT', body:JSON.stringify(d) }),
  delete: (pid,cid)=> api(`${SP_BASE}/posts/${pid}/comments/${cid}/`, { method:'DELETE' }),
  like  : (pid,cid)=> api(`${SP_BASE}/posts/${pid}/comments/${cid}/like/`, { method:'POST' }),
  unlike: (pid,cid)=> api(`${SP_BASE}/posts/${pid}/comments/${cid}/like/`, { method:'DELETE' }),
};

const NotifAPI = {
  list    : (p={}) => api(`${SP_BASE}/notifications/?${new URLSearchParams(p)}`),
  markRead: d => api(`${SP_BASE}/notifications/mark-read/`, { method:'POST', body:JSON.stringify(d) }),
  delete  : id => api(`${SP_BASE}/notifications/${id}/`, { method:'DELETE' }),
};

const TopicAPI = {
  list : () => api(`${SP_BASE}/topics/`),
  stats: () => api(`${SP_BASE}/stats/`),
};

const ResourceAPI = {
  list    : (p={}) => api(`${SP_BASE}/resources/?${new URLSearchParams(p)}`),
  byTopic : t => api(`${SP_BASE}/resources/topic/${t}/`),
  create  : d => api(`${SP_BASE}/resources/`, { method:'POST', body:JSON.stringify(d) }),
};

const ProgressAPI = {
  get   : () => api(`${SP_BASE}/progress/`),
  update: d => api(`${SP_BASE}/progress/update/`, { method:'POST', body:JSON.stringify(d) }),
};

// ─── Toast ────────────────────────────────────────────────────
function toast(msg, type = 'info', duration = 3500) {
  const el = document.createElement('div');
  el.className = `sp-toast sp-toast--${type}`;
  el.innerHTML = `<span class="sp-toast__icon">${{success:'✓',error:'✗',info:'◆',warning:'⚠'}[type]||'◆'}</span><span>${msg}</span>`;
  document.body.appendChild(el);
  requestAnimationFrame(() => el.classList.add('sp-toast--show'));
  setTimeout(() => {
    el.classList.remove('sp-toast--show');
    setTimeout(() => el.remove(), 400);
  }, duration);
}

// ─── Helpers ──────────────────────────────────────────────────
function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr);
  const s = Math.floor(diff/1000), m = Math.floor(s/60), h = Math.floor(m/60), d = Math.floor(h/24);
  if (s < 60) return 'just now';
  if (m < 60) return `${m}m ago`;
  if (h < 24) return `${h}h ago`;
  if (d < 7)  return `${d}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

function difficultyBadge(d) {
  const map = { beginner:'🟢', intermediate:'🟡', advanced:'🔴' };
  return `<span class="badge badge--${d}">${map[d]||'⚪'} ${d}</span>`;
}

function topicIcon(t) {
  const map = {
    serializers:'⚙', views:'👁', authentication:'🔐', permissions:'🛡',
    pagination:'📄', filtering:'🔍', validation:'✅', advanced:'🚀',
    best_practices:'⭐', troubleshooting:'🔧'
  };
  return map[t] || '🐍';
}

function extractErrors(data) {
  if (!data) return 'An error occurred.';
  if (typeof data === 'string') return data;
  const msgs = [];
  for (const [k, v] of Object.entries(data)) {
    const arr = Array.isArray(v) ? v : [v];
    arr.forEach(m => msgs.push(typeof m === 'object' ? extractErrors(m) : (k === 'non_field_errors' ? m : `${k}: ${m}`)));
  }
  return msgs.join(' • ');
}

// ─── Guard ────────────────────────────────────────────────────
function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = 'auth.html';
    return false;
  }
  return true;
}

function redirectIfAuthed() {
  if (Auth.isLoggedIn()) window.location.href = 'index.html';
}

// Export globally
window.SP = {
  Auth, UserAPI, PostAPI, CommentAPI, NotifAPI,
  TopicAPI, ResourceAPI, ProgressAPI,
  toast, timeAgo, difficultyBadge, topicIcon, extractErrors,
  requireAuth, redirectIfAuthed
};
