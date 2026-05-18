from django.shortcuts import render

def forbidden_view(request, exception=None):
    """
    Custom 403 Forbidden handler.
    Displays an alert and redirects to login.
    """
    return render(request, 'errors/403.html', status=403)
