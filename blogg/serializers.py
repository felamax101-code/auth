from rest_framework import serializers
from .models import Post,PollOption,PollVote,SavedPost

class PollOptionSerializer(serializers.ModelSerializer):
    vote_percentage=serializers.SerializerMethodField()
    class Meta:
        model=PollOption
        fields=["id","text","votes_count","vote_percentage","order"]
        read_only_fields=["votes_count"]
    def get_vote_percentage(self,obj):
        total=obj.poll_votes.count()
        if total==0:
            return 0
        return round((obj.votes_count/total)*100,1)
    
class PostSerializer(serislizer.ModelSerializer):
    author_username=serializers.CharField(source="author.username",read_only=True)
    author_avatar=serializers.ImageField(source="author.avatar",read_only=True)
    poll_options=PollOptionSerializer(many=True,read_only=True)
    has_voted=serializers.SerializerMethodField()
    is_liked=serializers.SerializerMethodField()
    original_post_data=serializers.SerializerMethodField()
    class Meta:
        model=Post
        fields=["id","author","author_username","author_avatar",
                "post_type","caption","language","image","video",
                "visibility","county","likes_count","comments_count",
                "reposts_count","saves_count","is_repost","original_post","original_post_data",
                "repost_caption","poll_options","has_voted","is_liked","is_saved",
                "created_at","updated_at"
                ]
        read_only_fields=["author","likes_count","comments_count",
                          "reposts_count","saves_count","created_at","updated_at"]
    def get_has_voted(self,obj):
        request=self.context.get('request')
        if not request or obj.post_type !=Post.PostType.POLL:
            return None
        return PollVote.objects.filter(user=request.user,post=obj).exists()
    def get_is_liked(self,obj):
        request=self.context.get("request")
        if not request:
            return False
        from apps.reactions.models import Reaction
        return Reaction.objects.filter(user=request.user,post=obj).exists()
    def get_is_saved(self,obj):
        request=self.context.get('request')
        if not request:
            return False
        return SavedPost.objects.filter(user=request.user,post=obj).exists()
    def get_original_post(self,obj):
        if obj.is_repost and obj.original_post:
            return{
                "id":obj.original_post_id,
                "author_username":obj.original_post.author.username,
                "caption":obj.original_post.caption,
                "post_type":obj.original_post.post_type,
                "image":obj.original_post.image.url if obj.original_post.image else None,
            }
        return None
    def validate(self,data):
        post_type=data.get('post_type')
        if post_type==Post.PostType.IMAGE and not data.get("image"):
            raise serializers.ValidationError(
                {"image":" Image post must include an image"}
            )
        if post_type==Post.PostType.VIDEO and not data.get("video"):
            raise serializers.ValidationError(
                {"video":" Vide post must include a video"})
        if data.get("visibility")==Post.Visibility.COUNTY and not data.get("county"):
            raise serializers.ValidationError({
                "county":"please provide a county"
            })
        return data
class CreatePostSerializer(serializer.ModelSerializer):
    poll_options=serializers.ListField(
        child=serializers.CharField(max_length=200),write_only=True,required=True
    )
    class Meta:
        model=Post
        fields=[
            "post_type","caption","language","image","video","visibility","county",
            "is_repost","original_post","repost_caption","post_options"
        ]
    def validate_poll_options(self,value):
        if len(value)<2:
            raise serializers.ValidationError("A poll must have at least two options.")
        if len(value)>4:
            raise serializers.ValidationError("A poll can have at most four options options.")
        return value
    def validate (self,data):
        post_type=data.get("post_type")
        if post_type==Post.PostType.POLL and not data.get("poll_options"):
            raise serializers.ValidationError(
            {"poll options":" Poll post must include options"}
        )
        if post_type==Post.PostType.IMAGE and not data.get("image"):
            raise serializers.ValidationError(
            {"poll options":" Poll post must include options"}
        )
        if post_type==Post.PostType.VIDEO and not data.get("video"):
            raise serializers.ValidationError(
            {"poll options":" Poll post must include options"}
        )
        if data.get("visibility")==Post.visibility.COUNTY and not data.get("county"):
            raise serializers.ValidationError({
                "county":" Please specify a county for county-inly posts"
            })
        return data
    def create(self,validated_data):
        poll_options=validated_data.pop("poll_options",[])
        post=Post.objects.create(**validated_data)
        
        for i,option_text in enumerate(poll_options):
            PolLOptions.objects.create(post=post,text=option_text,order=i)
        return post
    class PollVoteSerializer(serializers.ModelSerializer):
        class Meta:
            model=PollVote
            fields=["option"]
        def validate_option(self,value):
            post=self.context.get("post")
            if value.post!=post:
                raise serializers.ValidationError("this option does not belong to this poll")
            return value
        def validate(self,data):
            user=self.context["request"].user
            post=self.context["post"]
            
            if PollVote.objects.filter(user=user,post=post).exists():
                raise serializers.ValidationError("You have already voted on this poll")
            return data
        def create(self,validated_data):
            user=self.context["request"].user
            post=self.context["post"]
            option=validated_data["option"]
            vote=PollVote.objects.create(user=user,option=option,post=post)
            PollOption.objects.filter(pk=option.pk).update(votes_count=models.F("votes_count")+1)
            return vote
