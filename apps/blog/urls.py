from django.urls import path
from .views import PostListView, PostDetailView, PostCommentsView

urlpatterns = [
    # Posts endpoints
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    
    # Comments endpoints
    path('posts/<int:pk>/comments/', PostCommentsView.as_view(), name='post-comments'),
]