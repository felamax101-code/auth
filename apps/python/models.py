from django.db import models
from django.conf import settings
class Post(models.Model):
    title=models.CharField(max_length=200)
    series=models.CharField(max_length=100,blank=True,null=True)
    part=models.PositiveIntegerField(blank=True,null=True)
    body=models.TextField()
    
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="posts")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)
    
    class Meta:
        db_table="posts"
        ordering=["-created_at"]
        indexes=[
            models.Index(fields=["-created_at"]),
            models.Index(fields=["author","-created_at"]),
        ]
    def __str__(self):
        return f"{self.author} - {self.title}"
    
class Comment(models.Model):
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name="comments")
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="comments")
    text=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    is_pinned=models.BooleanField(default=False)
    is_edited=models.BooleanField(default=False)
    is_reported=models.BooleanField(default=False)
    class Meta:
        db_table="comments"
        ordering=["created_at"]
        indexes=[
            models.Index(fields=["post","created_at"]),
            models.Index(fields=["author","created_at"]),
        ]
    def __str__(self):
        return f"comment by {self.author} on {self.post}"
    
class CommentReply(models.Model):
    comment=models.ForeignKey(Comment,on_delete=models.CASCADE,related_name="replies")
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="comment_replies")
    text=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    is_edited=models.BooleanField(default=False)
    class Meta:
        db_table="comment_replies"
        ordering=["created_at"]
        indexes=[
            models.Index(fields=["comment","created_at"]),
            models.Index(fields=["author","created_at"]),
        ]
    def __str__(self):
        return f"reply by {self.author} on comment {self.comment_id}"
    
class CommentLike(models.Model):
    comment=models.ForeignKey(Comment,on_delete=models.CASCADE,related_name="likes")
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="comment_likes")
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table="comment_likes"
        unique_together=("comment","user")
    def __str__(self):
        return f"{self.user} likes comment {self.comment_id}"
class CommentReplyLike(models.Model):
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reply_likes")
    commentreply=models.ForeignKey(CommentReply,on_delete=models.CASCADE,related_name="reply_likes")
    created_at=models.DateTimeField(auto_now_add=True)
    is_edited=models.BooleanField(default=False)
    class Meta:
        unique_together="commentreply","author"
    def __str__(self):
        return f"{self.author.username} likes {self.commentreply}"
class Follow(models.Model):
    follower=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="following")
    following=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="followers")
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table="follows"
        unique_together=("follower","following")
    def __str__(self):
        return f"{self.follower} follows {self.following}"
class PostLike(models.Model):
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name="likes")
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="post_likes")
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table="post_likes"
        unique_together=("post","user")
    def __str__(self):
        return f"{self.user} likes post {self.post_id}"
class PostSave(models.Model):
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name="saves")
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="post_saves")
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table="post_saves"
        unique_together=("post","user")
    def __str__(self):
        return f"{self.user} saved post {self.post_id}"
    
class UserSocials(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="socials")
    youtube=models.CharField(blank=True,default="")
    github=models.CharField(blank=True,default="")
    linkedin=models.CharField(blank=True,default="")
    website=models.CharField(blank=True,default="")
class ExtraSocial(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="extra_socials")
    name=models.CharField(default="")
    url=models.CharField()