from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,permissions
from .models import Post,PollOption,PollVote,SavedPost
from .serializers import (PollOptionSerializer,PostSerializer,CreatePostSerializer,
                          PollVoteSerializer)
from .permissions import IsAuthorOrReadOnly
from .pagination import PostCursorPagination

class PostListView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        user=request.user
        queryset=Posts.objects.filter(is_active=True).select_related(
            "author","original_post__author"
        ).filter(models.Q(visibility=Post.visibility.PUBLIC)|
                 models.Q(visibility=Post.visibility.COUNTY,county=user.county)|
                 models.Q(author=user)).distinct()
        post_type=request.query_params.get("type")
        if post_type:
            queryset=queryset.filter(post_type=post_type)
        county=request.query_params.get("county")
        if county:
            queryset=queryset.filter(county__iexact=county)
        paginator=PostCursorPaginator()
        page=paginator.paginate_queryset(queryset,request)
        serializer=PostSerializer(page,many=True,context={"reqest":request})
        return paginator.get_paginated_response(serializer.data)
    def post(self,request):
        serializer=CreatePostSerializer(data=request.data,context={"request":request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,staus=status.HTTP_BAD_REQUEST)
class PostDetailView(APIView):
    permission_classes=[permissions.IsAuthenticated,IsAuthorReadOnly]
    def get_object(self,pk):
        post=get_object_or_404(Post,pk=pk,is_active=True)
        self.check_object_permissions(self.request,post)
        return post
    def get(self,request,pk):
        post=self.get_object(pk)
        serializer=PostSerializer(post,context={'request':request})
        return Response(serializer.data)
    def patch(self,request,pk):
        post=self.get_object(pk)
        serializer=PostSerializer(post,data=request.data,partiali=True,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.errors,status=status.HTTP_200_OK)
        return Response (serializer.errors,staus=status.HTTP_BAD_REQUEST)
    def delete(self,request,pk):
        post=self.get_object(pk)
        post.is_active=False
        post.save()
        return Reponse({
            "mesage":"Post deleted"
        },status=status.HTTP_NO_CONTENT)
class UserPostView(APIView):
    permission_classes=[permission.IsAuthenticated]
    def get(self,request,user_id):
        queryset=Post.objects.filter(author_id=user_id,
                                     is_active=True,
                                     ).select_related('author')
        paginator=PostCursorPaginator()
        page=paginator.paginate_queryset(queryset,request)
        serializer=PostSerializer(page,many=True,context={"request":request})
        return paginator.get_paginated_response(serializer.data)
    
class PollVoteView(APIView):
    permission_classes=[permission.IsAuthenticated]
    def get(self,request,post_id):
        post=get_object_or_404(Post,pk=post_id,post_type=Post.PostType.POLL,is_active=True)
        serializer=PollVoteSerializer(
            data=request.data,context={"request":request,"post":post}
        )
        if serializer.is_valid():
            serializer.save()
            post_serializer=PostSerializer(post,context={"request":request})
            return Response(post_serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class SavePostView(APIView):
    permission_classes=[permission.IsAuthenticated]
    def get(self,request):
        saved_ids=SavedPost.objects.filter(user=request.user).values_list("post_id",flat=True)
        queryset=Post.objects.filter(
             pk__in=saved_ids,
            is_active=True,
        ).select_related("author")
        paginator=PostCursorPaginator()
        page=paginator.paginate_queryset(queryset,request)
        serializer=PostSerializer(page,many=True,context={'request':request})
        return paginator.get_paginated_response(serializer.data)
class RepostView(APIView):
    permission_classes=[permission.IsAuthenticated]
    def post(self,request,post_id):
        original_post=get_object_or_404(Post,pk=post_id,is_active=True)
        if original_post.author==request.user:
            return Response({
                "error":"You cannot repost your own post"
            },status=status.HTTP_400_BAD_REQUEST)
        already_reposted=Post.objects.filter(
            author=request.user,
            is_repost=True,
            original_post=original_post
        ).exists()
        if already_reposted:
            return Response({
                "error":"You have already reposted this"
            },status=status.HTTP_400_BAD_REQUEST)
        repost_obJ=Post.objects.create(
            author=request.user,
            post_type=original_post.post_type,
            is_repost=True,
            original_caption=request.data.get("caption",""),
            visibility=Post.visibility.PUBLIC,
        )
        Post.objects.filter(pk=post_id).update(
            reposts_count=models.F("reposts_count"+1)
        )
        serializer=PostSerializer(repost_obj,context={"request":request})
        return Response(serializer.data,status=status.HTTP_200_CREATED)

    
