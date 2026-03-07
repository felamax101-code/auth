from rest_framework import permissions
from .models import Post, Comment, UserProgress


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow admins to edit, but allow anyone to read.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admins/staff
        return request.user and request.user.is_staff


class IsPostAuthorOrAdmin(permissions.BasePermission):
    """
    Permission to allow post authors and admins to edit/delete their posts.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for post author or admin
        return obj.author == request.user or request.user.is_staff


class IsCommentAuthorOrAdmin(permissions.BasePermission):
    """
    Permission to allow comment authors to edit/delete their comments.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for comment author or admin
        return obj.author == request.user or request.user.is_staff


class IsAuthenticatedForComments(permissions.BasePermission):
    """
    Permission to allow only authenticated users to comment.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Must be authenticated to comment
        return request.user and request.user.is_authenticated


class IsAuthenticated(permissions.BasePermission):
    """
    Permission to allow only authenticated users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdminOnly(permissions.BasePermission):
    """
    Permission to allow only admin/staff users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class CanEditPost(permissions.BasePermission):
    """
    Permission to allow editing posts (author or admin).
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff


class CanEditComment(permissions.BasePermission):
    """
    Permission to allow editing comments (author or admin).
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff


class CanDeleteComment(permissions.BasePermission):
    """
    Permission to allow deleting comments (author or admin).
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff


class IsCommentQuestionAuthor(permissions.BasePermission):
    """
    Permission to allow only the question author to mark answers.
    """
    def has_object_permission(self, request, view, obj):
        # obj is a comment
        # Check if current user is the author of the parent question
        if obj.parent_comment:
            return obj.parent_comment.author == request.user or request.user.is_staff
        return request.user.is_staff