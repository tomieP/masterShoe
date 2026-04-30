"""
Dashboard and reports views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    """
    Main dashboard view.
    """
    return render(request, 'dashboard/index.html')
