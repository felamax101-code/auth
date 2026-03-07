/**
 * SmartPythonists - Main Application JavaScript
 * Clean, organized, easy to debug
 */

// ================================================================
// CONFIG
// ================================================================
const CONFIG = {
    API_BASE: 'http://localhost:8000/api',
    TIMEOUT: 10000
};

// ================================================================
// STATE MANAGEMENT
// ================================================================
const STATE = {
    user: null,
    token: localStorage.getItem('accessToken'),
    discussions: [],
    resources: [],
    notifications: [],
    currentPage: 'home'
};

// ================================================================
// API CALLS
// ================================================================

async function apiCall(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE}${endpoint}`;
    
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };

    // Add auth token if available
    if (STATE.token) {
        defaultOptions.headers['Authorization'] = `Bearer ${STATE.token}`;
    }

    const finalOptions = { ...defaultOptions, ...options };

    try {
        console.log(`[API] ${finalOptions.method} ${endpoint}`);
        
        const response = await fetch(url, finalOptions);
        const data = await response.json();

        if (!response.ok) {
            console.error(`[API Error] ${response.status}:`, data);
            
            if (response.status === 401) {
                logoutUser();
                showModal('auth-modal');
            }
            
            throw new Error(data.detail || `HTTP ${response.status}`);
        }

        console.log(`[API] Success:`, data);
        return data;
    } catch (error) {
        console.error('[API Error]:', error);
        showNotification(error.message, 'error');
        throw error;
    }
}

// ================================================================
// AUTHENTICATION
// ================================================================

async function loginUser(email, password) {
    try {
        console.log('[Auth] Logging in:', email);
        
        const response = await apiCall('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        if (response.success) {
            // Store tokens
            localStorage.setItem('accessToken', response.access);
            localStorage.setItem('refreshToken', response.refresh);
            
            // Update state
            STATE.token = response.access;
            STATE.user = response.user;

            console.log('[Auth] Login successful:', STATE.user);
            
            // Hide modal and reload
            hideModal('auth-modal');
            showNotification('Signed in successfully!', 'success');
            
            // Refresh page to reload all data
            setTimeout(() => location.reload(), 500);
        }
    } catch (error) {
        console.error('[Auth] Login failed:', error);
        showNotification('Sign in failed: ' + error.message, 'error');
    }
}

async function registerUser(username, email, password) {
    try {
        console.log('[Auth] Registering:', email);
        
        const response = await apiCall('/auth/register/', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });

        if (response.success) {
            // Store tokens
            localStorage.setItem('accessToken', response.access);
            localStorage.setItem('refreshToken', response.refresh);
            
            // Update state
            STATE.token = response.access;
            STATE.user = response.user;

            console.log('[Auth] Registration successful:', STATE.user);
            
            // Hide modal and reload
            hideModal('auth-modal');
            showNotification('Account created successfully!', 'success');
            
            // Refresh page
            setTimeout(() => location.reload(), 500);
        }
    } catch (error) {
        console.error('[Auth] Registration failed:', error);
        showNotification('Registration failed: ' + error.message, 'error');
    }
}

function logoutUser() {
    console.log('[Auth] Logging out');
    
    // Clear state
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    STATE.token = null;
    STATE.user = null;

    // Update UI
    updateAuthButton();
    showNotification('Signed out', 'success');
    
    // Reload
    setTimeout(() => location.reload(), 500);
}

// ================================================================
// LOAD DATA
// ================================================================

async function loadDiscussions() {
    try {
        console.log('[Data] Loading discussions...');
        
        const response = await apiCall('/smartpythonists/posts/');
        STATE.discussions = response.results || [];

        console.log('[Data] Loaded discussions:', STATE.discussions.length);
        renderDiscussions();
    } catch (error) {
        console.error('[Data] Failed to load discussions:', error);
    }
}

async function loadResources() {
    try {
        console.log('[Data] Loading resources...');
        
        const response = await apiCall('/smartpythonists/resources/');
        STATE.resources = Array.isArray(response) ? response : response.results || [];

        console.log('[Data] Loaded resources:', STATE.resources.length);
        renderResources();
    } catch (error) {
        console.error('[Data] Failed to load resources:', error);
    }
}

async function loadNotifications() {
    if (!STATE.user) return;

    try {
        console.log('[Data] Loading notifications...');
        
        const response = await apiCall('/smartpythonists/notifications/');
        STATE.notifications = response.notifications || [];

        console.log('[Data] Loaded notifications:', STATE.notifications.length);
        updateNotificationBadge();
    } catch (error) {
        console.error('[Data] Failed to load notifications:', error);
    }
}

// ================================================================
// RENDER UI
// ================================================================

function renderDiscussions() {
    const container = document.getElementById('discussions-list');
    if (!container) return;

    if (STATE.discussions.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">No discussions yet</p>';
        return;
    }

    container.innerHTML = STATE.discussions.map(post => `
        <div class="card" onclick="viewDiscussion('${post.id}')">
            <div class="card-header">
                <div class="avatar">${post.author.username.substring(0, 2).toUpperCase()}</div>
                <div class="card-meta">
                    <div class="card-author">${post.author.username}</div>
                    <div class="card-time">${formatDate(post.published_at)}</div>
                </div>
            </div>
            
            <h3 class="card-title">${post.title}</h3>
            <p class="card-excerpt">${post.excerpt || post.content.substring(0, 100)}...</p>
            
            <div class="tag-group">
                ${post.tags.split(',').slice(0, 3).map(tag => `<span class="tag">${tag.trim()}</span>`).join('')}
            </div>
            
            <div class="card-footer">
                <span style="padding: 4px 8px; background: rgba(16,185,129,0.2); color: #10b981; border-radius: 4px; font-size: 0.75rem;">
                    ${post.difficulty}
                </span>
                <div style="display: flex; gap: 1rem;">
                    <span>💬 ${post.comments_count || 0}</span>
                    <span>👁️ ${post.views_count || 0}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function renderResources() {
    const container = document.getElementById('resources-list');
    if (!container) return;

    if (STATE.resources.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">No resources yet</p>';
        return;
    }

    container.innerHTML = STATE.resources.map(resource => `
        <div class="card">
            <h3 class="card-title">${resource.title}</h3>
            <p class="card-excerpt">${resource.description || ''}</p>
            
            <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 1rem; border-top: 1px solid var(--border);">
                <span style="font-size: 0.85rem; color: var(--text-muted);">
                    ⭐ ${resource.rating || '4.5'}/5
                </span>
                <a href="${resource.url}" target="_blank" class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.85rem;">
                    Learn →
                </a>
            </div>
        </div>
    `).join('');
}

async function viewDiscussion(postId) {
    try {
        console.log('[UI] Viewing discussion:', postId);
        
        const post = await apiCall(`/smartpythonists/posts/${postId}/`);
        
        const modal = document.getElementById('discussion-modal');
        const content = document.getElementById('discussion-detail');

        content.innerHTML = `
            <div style="padding-bottom: 2rem;">
                <h1 style="margin-bottom: 1rem;">${post.title}</h1>
                
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
                    <div class="avatar">${post.author.username.substring(0, 2).toUpperCase()}</div>
                    <div>
                        <div style="font-weight: 600;">${post.author.username}</div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">${formatDate(post.published_at)}</div>
                    </div>
                </div>

                <div style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 2rem;">
                    ${post.content}
                </div>

                <div style="display: flex; gap: 2rem; padding: 1rem; background: rgba(99,102,241,0.1); border-radius: 0.75rem; margin-bottom: 2rem;">
                    <span>💬 ${post.comments_count || 0} comments</span>
                    <span>👁️ ${post.views_count || 0} views</span>
                </div>

                ${STATE.user ? `
                    <form onsubmit="submitComment(event, '${postId}')">
                        <textarea id="comment-text" placeholder="Add your comment..." required></textarea>
                        <button type="submit" class="btn btn-primary">Post Comment</button>
                    </form>
                ` : `
                    <p style="text-align: center; color: var(--text-muted);">
                        <a href="#" onclick="showModal('auth-modal'); return false;">Sign in</a> to comment
                    </p>
                `}
            </div>
        `;

        showModal('discussion-modal');
    } catch (error) {
        console.error('[UI] Failed to load discussion:', error);
    }
}

async function submitComment(event, postId) {
    event.preventDefault();
    
    if (!STATE.user) {
        showModal('auth-modal');
        return;
    }

    const content = document.getElementById('comment-text').value;

    try {
        console.log('[API] Submitting comment');
        
        await apiCall(`/smartpythonists/posts/${postId}/comments/`, {
            method: 'POST',
            body: JSON.stringify({
                content,
                is_question: false,
                is_answer: false
            })
        });

        showNotification('Comment posted!', 'success');
        document.getElementById('comment-text').value = '';
        
        // Reload discussion
        viewDiscussion(postId);
    } catch (error) {
        console.error('[API] Failed to post comment:', error);
    }
}

// ================================================================
// NOTIFICATIONS
// ================================================================

function updateNotificationBadge() {
    const badge = document.querySelector('.badge');
    const unread = STATE.notifications.filter(n => !n.is_read).length;
    
    if (badge) {
        badge.textContent = unread;
        badge.style.display = unread > 0 ? 'block' : 'none';
    }
}

// ================================================================
// UI HELPERS
// ================================================================

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

function toggleAuthForm(event) {
    event.preventDefault();
    
    const loginForm = document.getElementById('login-form-container');
    const registerForm = document.getElementById('register-form-container');
    
    loginForm.classList.toggle('hidden');
    registerForm.classList.toggle('hidden');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#6366f1'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        z-index: 9999;
        max-width: 400px;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 4000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}

function updateAuthButton() {
    const btn = document.getElementById('auth-btn');
    if (!btn) return;

    if (STATE.user) {
        btn.textContent = `👤 ${STATE.user.username}`;
        btn.onclick = logoutUser;
    } else {
        btn.textContent = 'Sign In';
        btn.onclick = () => showModal('auth-modal');
    }
}

// ================================================================
// PAGE NAVIGATION
// ================================================================

document.addEventListener('click', (e) => {
    const navLink = e.target.closest('[data-page]');
    if (!navLink) return;

    e.preventDefault();
    
    const page = navLink.dataset.page;
    
    // Update active nav
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    navLink.classList.add('active');
    
    // Show page
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`${page}-page`).classList.add('active');
});

// ================================================================
// MODALS
// ================================================================

document.querySelectorAll('.modal-close').forEach(btn => {
    btn.onclick = (e) => {
        e.preventDefault();
        hideModal(btn.closest('.modal').id);
    };
});

// Authentication forms
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    await loginUser(email, password);
});

document.getElementById('register-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    await registerUser(username, email, password);
});

// Auth button
document.getElementById('auth-btn')?.addEventListener('click', (e) => {
    e.preventDefault();
    if (STATE.user) {
        logoutUser();
    } else {
        showModal('auth-modal');
    }
});

// Notifications
document.getElementById('notif-icon')?.addEventListener('click', () => {
    if (!STATE.user) {
        showModal('auth-modal');
        return;
    }
    
    loadNotifications();
    showModal('notifications-modal');
});

// Theme switcher
document.querySelectorAll('[data-theme]').forEach(btn => {
    btn.addEventListener('click', () => {
        const theme = btn.dataset.theme;
        document.body.classList.remove('theme-sunset', 'theme-ocean', 'theme-forest');
        if (theme !== 'default') {
            document.body.classList.add(`theme-${theme}`);
        }
        localStorage.setItem('theme', theme);
        
        document.querySelectorAll('[data-theme]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'default';
if (savedTheme !== 'default') {
    document.body.classList.add(`theme-${savedTheme}`);
    document.querySelector(`[data-theme="${savedTheme}"]`)?.classList.add('active');
}

// ================================================================
// INITIALIZATION
// ================================================================

function init() {
    console.log('[Init] SmartPythonists starting...');
    console.log('[Init] User:', STATE.user);
    console.log('[Init] Token:', STATE.token ? 'Present' : 'Missing');
    
    // Load initial data
    loadDiscussions();
    loadResources();
    
    if (STATE.token) {
        console.log('[Init] User authenticated');
        loadNotifications();
    }
    
    updateAuthButton();
    
    console.log('[Init] Ready!');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
