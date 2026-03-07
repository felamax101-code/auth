from django.contrib import admin

from .models import UserProgress,CommentLike,Ad,Resource,Notification,Post, Comment
admin.site.register( Post)
admin.site.register( Comment)
admin.site.register( Notification)
admin.site.register( Resource)
admin.site.register( CommentLike)
admin.site.register( Ad)

admin.site.register( UserProgress)




