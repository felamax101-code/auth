from django.urls import path
from .views import (
    PostSaveView,PostLikeView,PostDetailView,PostSearchView,
    PostListCreateView,OwnPostsView,UserPostsView,MentionUserView,
    UpdateSocialLinksView,OwnProfileView,OtherUsersProfileView,FollowUserView,
    CommentReportView,CommentReplyLikeView, CommentLikeView,CommentReplyCreateView,
    CommentCreateView,PostCreateView
)

urlpatterns=[
    path("posts/",PostCreateView.as_view(),name="post-list-create"),
    path("posts/search/",PostSearchView.as_view(),name="post-search"),
    path("posts/<int:id>/",PostDetailView.as_view(),name="post-detail"),
    path("posts/<int:id>/like/",PostLikeView.as_view(),name="post-like"),
    path("posts/<int:id>/save/",PostSaveView.as_view(),name="post-save"),
    path("posts/<int:id>/comments/",CommentCreateView.as_view(),name="post-comment-create"),
    path("users/<int:id>/follow/",FollowUserView.as_view(),name="follow-user"),
    path("comments/<int:id>/",CommentCreateView.as_view(),name="comment-detail"),
    path("comments/<int:id>/like/",CommentLikeView.as_view(),name="comment-like"),
    path("comments/<int:id>/replies/",CommentReplyCreateView.as_view(),name="comment-replies"),
    path("comments/replies/<int:id>/",CommentReplyCreateView.as_view(),name="comment-reply-detail"  ),
    path("comments/replies/<int:id>/like/",CommentReplyLikeView.as_view(),name="comment-reply-like"),
    path("comments/<int:id>/report/",CommentReportView.as_view(),name="comment-report"),
    path("users/<str:username>/",OtherUsersProfileView.as_view(),name="own-profile"),
    path("users/<str:username>/posts/",UserPostsView.as_view(),name="user-posts"),
    path("users/mention/",MentionUserView.as_view(),name="mention-user"),
    path("profile/view/",OwnProfileView.as_view(),name="own-profile-view"),
    path("profile/socials/",UpdateSocialLinksView.as_view(),name="socials"),
    path("profile/posts/",OwnPostsView.as_view(),name="Own-posts-view")
]