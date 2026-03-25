from django.contrib import admin
from .models import Post,Comment,CommentLike,CommentReply,PostLike,PostSave,Follow,CommentReplyLike,UserSocials,ExtraSocial
admin.site.register(CommentReplyLike)
admin.site.register(ExtraSocial)
admin.site.register(UserSocials)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'body')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'post', 'created_at')
    list_filter = ('created_at', 'author', 'post')
    search_fields = ('text',)

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('comment__text',)

@admin.register(CommentReply)
class CommentReplyAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'comment', 'created_at')
    list_filter = ('created_at', 'author', 'comment')
    search_fields = ('text',)

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('post__title',)

@admin.register(PostSave)
class PostSaveAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('post__title',)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at', 'follower', 'following')
    search_fields = ('follower__username', 'following__username')
