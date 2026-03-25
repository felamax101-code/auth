from rest_framework import serializers
from .models import Post,Comment,CommentLike,CommentReply,Follow,CommentReplyLike,UserSocials,ExtraSocial
from apps.authe.models import CustomUser
User=CustomUser
class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'series', 'part', 'body']
    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Title is required")
        return value
    def validate(self,data):
        series=data.get("series")
        part=data.get("part")
        if (series and not part) or (part and not series):
            raise serializers.ValidationError("Both series and part must be provided together.")
        return data
    def create(self,validated_data):
        user=self.context['request'].user
        validated_data['author'] = user
        return Post.objects.create(**validated_data)
class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields=["title","series","part","body"]
    def validate(self,data):
        title=data.get("title")
        if title is not None and not title.strip():
            raise serializers.ValidationError({"title":"Title cannot be empty"})
        series=data.get("series")
        part=data.get("part")
        if (series and not part) or (part and not series):
            raise serializers.ValidationError("Both series and part must be provided together.")
        return data
class CommentReplySerializer(serializers.ModelSerializer):
    is_liked=serializers.SerializerMethodField()
    likes_count=serializers.SerializerMethodField()
    author=serializers.SerializerMethodField()
    class Meta:
        model=CommentReply
        fields=["id","text","created_at","is_edited","is_liked","likes_count","author"]
    def get_is_liked(self,obj):
        request=self.context.get("request")
        if not request:
            return False
        return CommentReplyLike.objects.filter(author=request.user,commentreply=obj).exists()
    def get_likes_count(self,obj):
        return CommentReplyLike.objects.filter(commentreply=obj).count()
    def get_author(self,obj):
        return {
            "id":obj.author.id,
            "username":obj.author.username,
        }
    def validate_text(self,value):
        if not value or not value.strip():
            raise serializers.ValidationError("Reply text cannot be empty")
        return value
    def create(self, validated_data):
        request = self.context.get("request")
        comment = self.context.get("comment")

        reply = CommentReply.objects.create(
        author=request.user,
        comment=comment,
        **validated_data
    )
        return reply
class CommentSerializer(serializers.ModelSerializer):
    
    is_liked=serializers.SerializerMethodField()
    likes_count=serializers.SerializerMethodField()
    replies=CommentReplySerializer(many=True,read_only=True)
    author=serializers.SerializerMethodField(read_only=True)
    class Meta:
        model=Comment
        fields=["id","text","created_at","is_edited","is_liked","likes_count","is_pinned","author","replies"]
        

  
   
  

    def get_is_liked(self,obj):
        request=self.context.get("request")
        if not request:
            return False
        return CommentLike.objects.filter(user=request.user,comment=obj).exists()
    def get_author(self,obj):
        return {
            "id":obj.author.id,
            "username":obj.author.username,
        }
    def get_likes_count(self,obj):
        return CommentLike.objects.filter(comment=obj).count()
    def validate(self,data):
        text=data.get("text")
        if not text or not text.strip():
            raise serializers.ValidationError({"text":"Comment text cannot be empty"})
        return data
    def create(self,validated_data):
        post=self.context.get('post')
        user=self.context['request'].user
        validated_data['author']=user
        return Comment.objects.create(post=post,**validated_data)
class OthersProfileSerializer(serializers.ModelSerializer):
    is_following=serializers.SerializerMethodField()
    followers_count=serializers.IntegerField(source="followers.count",read_only=True)
    following_count=serializers.IntegerField(source="following.count",read_only=True)
    post_count=serializers.IntegerField(source="posts.count",read_only=True)
    socials=serializers.SerializerMethodField()
    extra_socials=serializers.SerializerMethodField()
    class Meta:
        model=CustomUser
        fields=["id","username","bio","followers_count","following_count","post_count","is_following","socials","extra_socials"]
    def get_is_following(self,obj):
        request=self.context.get("request")
        if not request:
            return False
        return Follow.objects.filter(follower=request.user,following=obj).exists()
    def get_socials(self, obj):
        try:
            s = obj.socials  # reverse OneToOne
            return { "youtube": s.youtube, "github": s.github, "linkedin": s.linkedin, "website": s.website }
        except UserSocials.DoesNotExist:
            return { "youtube": "", "github": "", "linkedin": "", "website": "" }

    def get_extra_socials(self, obj):
        return list(obj.extra_socials.values("id", "name", "url"))
class OwnProfileSerializer(serializers.ModelSerializer):
    socials       = serializers.SerializerMethodField()
    extra_socials = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    def get_socials(self, obj):
        try:
            s = obj.socials  # reverse OneToOne
            return { "youtube": s.youtube, "github": s.github, "linkedin": s.linkedin, "website": s.website }
        except UserSocials.DoesNotExist:
            return { "youtube": "", "github": "", "linkedin": "", "website": "" }

    def get_extra_socials(self, obj):
        return list(obj.extra_socials.values("id", "name", "url"))

    def get_followers_count(self, obj):
        return obj.followers.count()

    class Meta:
        model  = CustomUser
        fields = ["id", "username", "email", "phone", "followers_count", "socials", "extra_socials"]
class ChangeUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=["username"]
    def validate_username(self,value):
        if not value or not value.strip():
            raise serializers.ValidationError("Username cannot be empty")
        if CustomUser.objects.filter(username=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Username already taken Try another one")
        return value
    def update(self,instance,validated_data):
        instance.username=validated_data.get("username",instance.username)
        instance.save()
        return instance
class ExtraSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model=ExtraSocial
        fields=["id","name","url"]
class UserSocialsSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserSocials
        fields=["youtube","linkedin","github","website"]
class UpdateSocialSerializer(serializers.Serializer):
    youtube=serializers.CharField(required=False,allow_blank=True,default="")
    github=serializers.CharField(required=False,allow_blank=True,default="")
    linkedin=serializers.CharField(required=False,allow_blank=True,default="")
    website=serializers.CharField(required=False,allow_blank=True,default="")
    extra_socials=ExtraSocialSerializer(many=True,required=False,default=list)
    class Meta:
        model=CustomUser
        fields=["youtube","linkedin","github","website","extra_socials"]
    

class AuthorSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()

    def get_is_following(self, obj):
        user = self.context["request"].user
        return obj.followers.filter(id=user.id).exists()

    class Meta:
        model  = User
        fields = ["id", "username", "is_following"]
class PostSerializer(serializers.ModelSerializer):
    is_liked      = serializers.SerializerMethodField()
    is_saved      = serializers.SerializerMethodField()
    likes_count   = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    author        = AuthorSerializer(read_only=True)
    read_time     = serializers.SerializerMethodField()

    def get_is_liked(self, obj):
        user = self.context["request"].user
        return obj.likes.filter(user=user).exists()

    def get_is_saved(self, obj):
        user = self.context["request"].user
        return obj.saves.filter(user=user).exists()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_read_time(self, obj):
        word_count = len(obj.body.split())
        return max(1, round(word_count / 200))

    class Meta:
        model  = Post
        fields = ["id", "title", "body", "series", "part", "read_time",
                  "created_at", "is_liked", "is_saved", "likes_count",
                  "comments_count", "author"]