from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer, PostListSerializer


class PostListView(APIView):
    """
    GET /api/posts/ - List all posts
    POST /api/posts/ - Create new post (admin only)
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all posts"""
        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create new post (admin only)"""
        # Check if user is admin
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can create posts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """
    GET /api/posts/{id}/ - Get single post
    PUT /api/posts/{id}/ - Update post (admin only)
    DELETE /api/posts/{id}/ - Delete post (admin only)
    """
    permission_classes = [AllowAny]
    
    def get_object(self, pk):
        """Get post by ID or return 404"""
        return get_object_or_404(Post, pk=pk)
    
    def get(self, request, pk):
        """Get single post with comments"""
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Update post (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can update posts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post = self.get_object(pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Delete post (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can delete posts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        post = self.get_object(pk)
        post.delete()
        return Response(
            {'message': 'Post deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


class PostCommentsView(APIView):
    """
    GET /api/posts/{id}/comments/ - Get all comments for a post
    POST /api/posts/{id}/comments/ - Create comment on a post
    """
    permission_classes = [AllowAny]
    
    def get_post(self, pk):
        """Get post by ID or return 404"""
        return get_object_or_404(Post, pk=pk)
    
    def get(self, request, pk):
        """Get all comments for a post"""
        post = self.get_post(pk)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        """Create new comment on a post"""
        post = self.get_post(pk)
        
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)