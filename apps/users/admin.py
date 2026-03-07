from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, TokenBlacklist, LoginAudit


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    
    list_display = [
        'email', 'username', 'role', 'is_email_verified',
        'is_active', 'is_locked', 'date_joined', 'last_login_at'
    ]
    list_filter = ['role', 'is_active', 'is_email_verified', 'is_locked', 'date_joined']
    search_fields = ['email', 'username', 'phone']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Personal Info', {'fields': ('email', 'username', 'phone', 'profile_picture')}),
        ('Status', {'fields': ('is_active', 'is_email_verified', 'is_deactivated')}),
        ('Security', {
            'fields': (
                'is_locked', 'failed_attempts', 'locked_until',
                'force_password_reset', 'last_login_ip', 'last_login_at'
            ),
            'classes': ('collapse',)
        }),
        ('Email Verification', {
            'fields': ('email_verification_token', 'email_verification_token_expires'),
            'classes': ('collapse',)
        }),
        ('Password Reset', {
            'fields': ('password_reset_token', 'password_reset_token_expires'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('date_joined', 'last_time_updated'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['date_joined', 'last_time_updated', 'last_login_at']
    
    actions = ['force_password_reset_action', 'unlock_account_action', 'deactivate_action']
    
    def force_password_reset_action(self, request, queryset):
        """Force password reset for selected users"""
        updated = queryset.update(force_password_reset=True)
        self.message_user(request, f'Forced password reset for {updated} user(s).')
    force_password_reset_action.short_description = 'Force password reset'
    
    def unlock_account_action(self, request, queryset):
        """Unlock selected accounts"""
        updated = queryset.update(is_locked=False, failed_attempts=0, locked_until=None)
        self.message_user(request, f'Unlocked {updated} account(s).')
    unlock_account_action.short_description = 'Unlock accounts'
    
    def deactivate_action(self, request, queryset):
        """Deactivate selected accounts"""
        updated = queryset.update(is_active=False, is_deactivated=True)
        self.message_user(request, f'Deactivated {updated} account(s).')
    deactivate_action.short_description = 'Deactivate accounts'


@admin.register(TokenBlacklist)
class TokenBlacklistAdmin(admin.ModelAdmin):
    """Token blacklist admin"""
    
    list_display = ['user', 'blacklisted_at', 'expires_at', 'is_expired']
    list_filter = ['blacklisted_at', 'expires_at']
    search_fields = ['user__email', 'token']
    ordering = ['-blacklisted_at']
    readonly_fields = ['user', 'token', 'blacklisted_at', 'expires_at']
    
    def is_expired(self, obj):
        """Show if token is expired"""
        from django.utils import timezone
        expired = timezone.now() > obj.expires_at
        color = 'red' if expired else 'green'
        status_text = 'Expired' if expired else 'Active'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            status_text
        )
    is_expired.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LoginAudit)
class LoginAuditAdmin(admin.ModelAdmin):
    """Login audit log admin"""
    
    list_display = ['email_attempted', 'status', 'ip_address', 'attempted_at', 'user']
    list_filter = ['status', 'attempted_at']
    search_fields = ['email_attempted', 'ip_address', 'user__email']
    ordering = ['-attempted_at']
    readonly_fields = [
        'user', 'email_attempted', 'ip_address', 'status',
        'reason', 'user_agent', 'attempted_at'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser