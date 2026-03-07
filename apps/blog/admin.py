from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'created_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Post Info', {
            'fields': ('title', 'content', 'difficulty')
        }),
        ('Social Media Links', {
            'fields': ('youtube_url', 'tiktok_url', 'facebook_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    list_filter = ['created_at', 'post']
    search_fields = ['author', 'text']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Comment Info', {
            'fields': ('post', 'author', 'text')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )