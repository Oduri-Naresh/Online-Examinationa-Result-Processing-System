from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def student_required(view):
    @login_required
    def wrap(request, *args, **kwargs):
        if request.user.profile.role != 'student':
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrap


def faculty_required(view):
    @login_required
    def wrap(request, *args, **kwargs):
        profile = request.user.profile
        if profile.role != 'faculty' or profile.approval_status != 'Approved':
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrap


def admin_required(view):
    @login_required
    def wrap(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrap
