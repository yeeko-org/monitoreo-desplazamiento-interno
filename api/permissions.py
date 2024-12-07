from rest_framework.permissions import BasePermission, SAFE_METHODS

from note.models import NoteContent


class IsFullEditorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_anonymous:
            return False

        if request.user.is_superuser or request.user.full_editor:
            return True


class IsAuthenticatedOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.user.is_anonymous:
            return False

        return True


class ByStatusOrReadOnly(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj: NoteContent):
        if request.method in SAFE_METHODS:
            return True

        if obj.status_register_id == "draft":
            return True

        return request.user.full_editor or request.user.is_superuser
