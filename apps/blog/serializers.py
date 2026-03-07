from rest_framework import serializers
from apps.blog.models import Post,Comment
from django.contrib.auth import get_user_model
User=get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields=["id","author","text","created_at"]
        read_only_fields=["id","created_at"]
        
class PostSerializer(serializers.ModelSerializer):
    comments=CommentSerializer(many=True,read_only=True)
    class Meta:
        model=Post
        fields=["id","title",
                "content","difficulty",
                "youtube_url","tiktok_url",
                "facebook_url","created_at",
                "updated_at","comments"]
        read_only_fields=["id","created_at",
                "updated_at"]
class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields=["id","title",
                "content","difficulty",
                "youtube_url","tiktok_url",
                "facebook_url","created_at"]