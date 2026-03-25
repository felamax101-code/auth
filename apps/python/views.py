from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,permissions
from .serializers import (CreatePostSerializer,UpdatePostSerializer,
CommentSerializer,CommentReplySerializer,OthersProfileSerializer,
ChangeUsernameSerializer,UpdateSocialSerializer,
PostSerializer,OwnProfileSerializer)
from django.shortcuts import get_object_or_404
from .models import Post,Comment,CommentLike,CommentReply,PostLike,PostSave,Follow,UserSocials,ExtraSocial,CommentReplyLike
from django.db.models import Count,Q
from apps.authe.models import CustomUser as User
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
class PostCreateView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self, request):
        tab = request.GET.get("tab", "all")
        page = int(request.GET.get("page", 1))

        posts = Post.objects.filter(is_active=True).order_by("-created_at")

        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page)

        serializer = PostSerializer(
            page_obj,
            many=True,
            context={"request": request}
        )

        return Response({
            "results": serializer.data,
            "has_more": page_obj.has_next(),
            "next_page": page + 1 if page_obj.has_next() else None
        }, status=status.HTTP_200_OK)
    def post(self,request):
        serializer=CreatePostSerializer(data=request.data,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "id":serializer.instance.id,
                "message": "Post created successfully"
            },status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def patch(self,request,pk):
        post=Post.objects.get(pk=pk,author=request.user)
        if not post:
            return Response({"detail":"Post not found"},status=status.HTTP_404_NOT_FOUND)
        serializer=UpdatePostSerializer(post,data=request.data,partial=True,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        post=Post.objects.get(pk=pk,author=request.user)
        if not post:
            return Response({"detail":"Post not found"},status=status.HTTP_404_NOT_FOUND)
        post.is_active=False
        post.save()
        return Response({"detail":"Post deleted"},status=status.HTTP_204_NO_CONTENT)
    
class CommentCreateView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request,id):
        post=Post.objects.get(pk=id,is_active=True)
        if not post:
            return Response({"detail":"Post not found"},status=status.HTTP_404_NOT_FOUND)
        comments=Comment.objects.filter(post=post).order_by("-created_at")
        serializer=CommentSerializer(comments,many=True,context={"request":request})
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self,request,id):
        post=Post.objects.get(pk=id,is_active=True)
        if not post:
            return Response({"detail":"Post not found"},status=status.HTTP_404_NOT_FOUND)
        serializer=CommentSerializer(data=request.data,context={"request":request,"post":post})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def put(self,id):
        comment=Comment.objects.get(pk=id,author=request.user)
        if not comment:
            return Response({"detail":"Comment not found"},status=status.HTTP_404_NOT_FOUND)
        serializer=CommentSerializer(comment,data=request.data,partial=True,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Comment updated successfully"
            },status=status.HTTP_200_OK)
        comment.is_edited=True
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,id):
        comment=Comment.objects.get(pk=id,author=request.user)
        if not comment:
            return Response({"detail":"Comment not found"},status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response({"detail":"Comment deleted"},status=status.HTTP_204_NO_CONTENT)
class CommentReplyCreateView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request,id):
        comment=Comment.objects.get(pk=id)
        if not comment:
            return Response({"detail":"Comment not found"},status=status.HTTP_404_NOT_FOUND)
        serializer=CommentReplySerializer(data=request.data,context={"request":request,"comment": comment})
        if serializer.is_valid():
            serializer.save(
                
            )
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def put(self,request,id):
        reply=CommentReply.objects.get(pk=id,author=request.user)
        if not reply:
            return Response({"detail":"Reply not found"},status=status.HTTP_404_NOT_FOUND)
        serializer=CommentReplySerializer(reply,data=request.data,partial=True,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Reply updated successfully"
            },status=status.HTTP_200_OK)
        reply.is_edited=True
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,id):
        reply=CommentReply.objects.get(pk=id,author=request.user)
        if not reply:
            return Response({"detail":"Reply not found"},status=status.HTTP_404_NOT_FOUND)
        reply.delete()
        return Response({"detail":"Reply deleted"},status=status.HTTP_204_NO_CONTENT)
class CommentLikeView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request,id):
        comment=Comment.objects.get(pk=id)
        if not comment:
            return Response({"detail":"Comment not found"},status=status.HTTP_404_NOT_FOUND)
        like,created=CommentLike.objects.get_or_create(user=request.user,comment=comment)
        if created:
            likes_count=CommentLike.objects.filter(comment=comment).count()
            return Response({"liked":True,"likes_count":likes_count},status=status.HTTP_200_OK)
        like.delete()
        likes_count=CommentLike.objects.filter(comment=comment).count()
        return Response({"liked":False,"likes_count":likes_count},status=status.HTTP_200_OK)
class CommentReplyLikeView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request,id):
        reply=CommentReply.objects.get(pk=id)
        if not reply:
            return Response({"detail":"Reply not found"},status=status.HTTP_404_NOT_FOUND)
        like,created=CommentReplyLike.objects.get_or_create(author=request.user,commentreply=reply)
        if created:
            likes_count=CommentReplyLike.objects.filter(commentreply=reply).count()
            return Response({"liked":True,"likes_count":likes_count},status=status.HTTP_200_OK)
        like.delete()
        likes_count=CommentReplyLike.objects.filter(commentreply=reply).count()
        return Response({"liked":False,"likes_count":likes_count},status=status.HTTP_200_OK)
class CommentReportView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request,id):
        comment=Comment.objects.get(pk=id)
        if not comment:
            return Response({"detail":"Comment not found"},status=status.HTTP_404_NOT_FOUND)
        comment.is_reported=True
        comment.save()
        return Response({"detail":"Comment reported"},status=status.HTTP_200_OK)
class FollowUserView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request,id):
        user_to_follow=get_object_or_404(User,pk=id,is_active=True)
        if user_to_follow==request.user:
            return Response({"detail":"You cannot follow yourself"},status=status.HTTP_400_BAD_REQUEST)
        follow,created=Follow.objects.get_or_create(follower=request.user,following=user_to_follow)
        if created:
            followers_count=Follow.objects.filter(following=user_to_follow).count()
            if followers_count==0:
                followers_count=0
            return Response({"following":True,"followers_count":followers_count},status=status.HTTP_200_OK)
        follow.delete()
        followers_count=Follow.objects.filter(following=user_to_follow).count()
        if followers_count==0:
            followers_count=0
        return Response({"following":False,"followers_count":followers_count},status=status.HTTP_200_OK)
class OtherUsersProfileView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request,username):
        user=get_object_or_404(User,username=username,is_active=True)
        serializer=OthersProfileSerializer(user,context={"request":request})
        return Response(serializer.data,status=status.HTTP_200_OK)
class OwnProfileView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        serializer=OwnProfileSerializer(request.user,context={"request":request})
        return Response(serializer.data,status=status.HTTP_200_OK)
    def put (self,request):
        serializer=ChangeUsernameSerializer(instance=request.user,data=request.data,partial=True,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Username updated successfully"
            }, status=status.HTTP_200_OK)
        return Response({
            "message": serializer.errors
        },status=status.HTTP_400_BAD_REQUEST)
class UpdateSocialLinksView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateSocialSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        user = request.user

        # Update or create the fixed socials row
        socials, _ = UserSocials.objects.get_or_create(user=user)
        socials.youtube  = data.get("youtube",  "")
        socials.github   = data.get("github",   "")
        socials.linkedin = data.get("linkedin", "")
        socials.website  = data.get("website",  "")
        socials.save()

        # Replace extra socials entirely
        # Delete old ones, create new ones from the incoming list
        ExtraSocial.objects.filter(user=user).delete()
        for item in data.get("extra_socials", []):
            ExtraSocial.objects.create(
                user=user,
                name=item["name"],
                url=item["url"],
            )

        return Response({"message": "Social links updated."})  
class MentionUserView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        q=request.query_params.get("q","").strip()
        if not q:
            return Response({"detail":"Query parameter is required"},status=status.HTTP_400_BAD_REQUEST)
        users=User.objects.filter(
            username__istartswith=q,
            is_active=True
        ).exclude(id=request.user.id).values("id","username")[:8]
        return Response({
            "results": list(users)
        })
        
class UserPostsView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request,username):
        try :
            user=User.objects.get(username=username,is_active=True)
        except User.DoesNotExist:
            return Response({"detail":"User not found"},status=status.HTTP_404_NOT_FOUND)
        page=int(request.query_params.get("page",1))
        page_size=10
        posts=Post.objects.filter(author=user,is_active=True).order_by("-created_at")
        total_posts=posts.count()
        start=(page-1)*page_size
        end=start+page_size
        results=posts[start:end]
        serializer=PostSerializer(results,many=True,context={"request":request})
        return Response({
            "results": serializer.data,
            "has_more": end<total_posts
        })
class OwnPostsView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        page=int(request.query_params.get("page",1))
        page_size=10
        posts=Post.objects.filter(author=request.user,is_active=True).order_by("-created_at")
        total_posts=posts.count()
        start=(page-1)*page_size
        end=start+page_size
        results=posts[start:end]
        serializer=PostSerializer(results,many=True,context={"request":request})
        return Response({
            "results": serializer.data,
            "has_more": end<total_posts
        })
        
class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tab      = request.query_params.get("tab", "all").lower()
        page     = int(request.query_params.get("page", 1))
        page_size = 10

        if tab == "following":
            posts = Post.objects.filter(
                author__in=request.user.following.all()
            ).order_by("-created_at")

        elif tab == "trending":
            posts = Post.objects.annotate(
                score=Count("likes") * 3 + Count("comments") * 2
            ).order_by("-score", "-created_at")

        elif tab == "saved":
            posts = Post.objects.filter(
                saves__user=request.user
            ).order_by("-created_at")

        else:  # "all"
            posts = Post.objects.all().order_by("-created_at")

        total   = posts.count()
        start   = (page - 1) * page_size
        end     = start + page_size
        results = posts[start:end]

        return Response({
            "results":   PostSerializer(results, many=True, context={"request": request}).data,
            "has_more":  end < total,
            "next_page": page + 1 if end < total else None,
        })

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            post = serializer.save(author=request.user)
            return Response({ "id": post.id, "message": "Post published." }, status=201)
        return Response(serializer.errors, status=400)
class PostSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q         = request.query_params.get("q", "").strip()
        page      = int(request.query_params.get("page", 1))
        page_size = 10

        if not q:
            return Response({ "results": [], "has_more": False })

        # Basic ORM search — swap for PostgreSQL FTS when ready
        posts = Post.objects.filter(
            Q(title__icontains=q) |
            Q(body__icontains=q)  |
            Q(author__username__icontains=q) |
            Q(series__icontains=q)
        ).order_by("-created_at")

        total   = posts.count()
        start   = (page - 1) * page_size
        end     = start + page_size
        results = posts[start:end]

        return Response({
            "results":  PostSerializer(results, many=True, context={"request": request}).data,
            "has_more": end < total,
        })
class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response({ "detail": "Post not found." }, status=404)
        return Response(PostSerializer(post, context={"request": request}).data)
class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response({ "detail": "Post not found." }, status=404)

        like, created = PostLike.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()  # already liked → unlike
            liked = False
        else:
            liked = True

        return Response({
            "liked":       liked,
            "likes_count": post.likes.count(),
        })
class PostSaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response({ "detail": "Post not found." }, status=404)

        save, created = PostSave.objects.get_or_create(user=request.user, post=post)
        if not created:
            save.delete()  # already saved → unsave
            saved = False
        else:
            saved = True

        return Response({ "saved": saved })