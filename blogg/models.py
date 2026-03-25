from django.db import models
from django.config import settings

class Post(models.Model):
    class PostType(models.TextChoices):
        TEXT='text','Text'
        IMAGE="image","Image"
        VIDEO="video","Video"
        POLL='poll',"Poll"
    class Visibility(models.TextChoices):
        PUBLIC="public","Public"
        COUNTY="county","County"
        FOLLOWERS="followers","Followers"
    class Language(models.TextChoices):
        EBGLISH="english","English"
        SWAHILI="swahili","Swahili"
        SHENG="sheng","Sheng"
        OTHER="other","Other"
    author=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    post_type=models.CharField(
        max_length=10,
        choices=PostType.choices,
        default=PostType.TEXT
    )
    caption=models.TextField(blank=True)
    language=models.CharField(
        max_length=10,
        choices=Language.choices,
        default=Language.ENGLISH
    )
    image=models.ImageFied(
        upload_to="posts,images,%Y/%m",
        null=True,blank=True
    )
    video=models.FileField(
        upload_to="posts/video/%Y/%m",
        null=True,blank=True
    )
    visibility=models.CharField(
        max_length=10,
        choices=Visibility.choices,default=Visibility.PUBLIC
    )
    county=models.CharField(
        max_length=10,
        blank=True,
        help_text="if visibility is county,which county"
    )
    likes_count=models.PositiveIntegerField(default=0)
    comments_count=models.PositiveIntegerField(default=0)
    reposts_count=models.PositiveIntegerField(default=0)
    saves_count=models.PositiveIntegerField(default=0)
    
    is_repost=models.BooleanField(default=False)
    original_post=models.ForeignKey("self",
                                    null=True,
                                    on_delete=models.SET_null,
                                    related_name="reposts")
    repost_caption=models.TextField(blank=True)
    
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'posts'
        ordering=["-created_at-"]
        indexes=[
            models.Index(fields=["-created_at-"]),
            models.Index(fields=["author","-created_at-"]),
            models.Index(fields=["visibility","county"]),
            models.Index(fields=["post_type"]),
        ]
    def __str__(self):
        return f"{self.author} - {self.post_type} - {self.created_at.date()}"
class PollOption(models.Model):
    post=models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="poll_options"
    )
    text=models.CharField(max_length=200)
    votes_count=models.PositiveIntegerField(default=0)
    order=models.PositiveIntegerField(default=0)
    class Meta:
        db_table="poll_options"
        ordering=["order"]
        
        def __str__(self):
            return f"{self.post_id} - {self.text}"
class PollVote(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,
                           on_delete=models.CASCADE,
                           related_names="poll_votes")
    option=models.ForeignKey(PollOption,
                             on_delete=models.CASCADE,
                             related_name="poll_votes"
                             )
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table="poll_votes"
        unique_together=("user","post")
    def __str__(self):
        return f"{self.user} voted on post {self.post_id}"
    
class SavedPost(models.Models):
    user=models.ForeignKey(
        settings.AUTH_USER_MODELS,
        on_delete=models.CASCADE,
        related_name="saved_posts"
    )
    post=models.ForeighnKey(
        Post,
        on_delete=models.CASCADE,
        related_name="saved_by"
    )
    created_at=models.DteTimeField(auto_now_add=True)
    class Meta:
        db_table="saved_posts"
        unique_together=("user","post")
        ordering=["-created_at-"]
        
