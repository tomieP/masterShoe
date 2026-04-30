from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseForbidden


def staff_required(view_func):
    """
    Allows access for staff and manager (and superusers).
    Redirects to login if not authenticated.
    Returns 403 if authenticated but not in staff/manager group.
    """
    def _wrapped_view(request, *args, **kwargs):
        # Handle cases where user is None or AnonymousUser
        if not hasattr(request, 'user') or request.user is None or isinstance(request.user, AnonymousUser):
            return redirect_to_login(request.get_full_path())
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        # Check if user is in Staff or Manager group, or is superuser
        if request.user.groups.filter(name__in=['Staff', 'Manager']).exists() or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return _wrapped_view


def manager_required(view_func):
    """
    Allows access for manager only (and superusers).
    Redirects to login if not authenticated.
    Returns 403 if authenticated but not in manager group.
    """
    def _wrapped_view(request, *args, **kwargs):
        # Handle cases where user is None or AnonymousUser
        if not hasattr(request, 'user') or request.user is None or isinstance(request.user, AnonymousUser):
            return redirect_to_login(request.get_full_path())
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return _wrapped_view


def manager_or_staff_required(view_func):
    """
    Allows access for either staff or manager (and superusers).
    This is equivalent to staff_required.
    Redirects to login if not authenticated.
    Returns 403 if authenticated but not in staff/manager group.
    """
    return staff_required(view_func)