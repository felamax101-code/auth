from django.db import models
class Post(models.Model):
    DIFFICULTY_CHOICES=[
        ("Beginner","Beginner"),
         ("Intermediate","Intermediate"),
          ("Advanced","Advanced"),
    ]
    title=models.CharField(max_length=200)
    content=models.TextField()
    difficulty=models.CharField(choices=DIFFICULTY_CHOICES,max_length=20,default="Beginner")
    youtube_url=models.URLField(blank=True,null=True)
    tiktok_url=models.URLField(blank=True,null=True)
    facebook_url=models.URLField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']
    
    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name="comments")
    author=models.CharField(max_length=100,blank=True,default="Anonymous")
    text=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']
        
    def __str__(self):
        return f"comment by {self.author} on {self.post.title}"
        
    
        