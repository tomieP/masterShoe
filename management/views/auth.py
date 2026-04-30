"""
Authentication views for user login and logout.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handle user login.

    GET: Display login form
    POST: Validate credentials and log user in
    """
    # Redirect already authenticated users to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                from django.contrib import messages
                messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    else:
        form = AuthenticationForm()

    # Add Bootstrap classes to form fields
    for field_name, field in form.fields.items():
        field.widget.attrs['class'] = 'form-control'
        field.widget.attrs['placeholder'] = field.label

    return render(request, 'auth/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    Handle user logout.

    Logs out the user and redirects to login page.
    """
    logout(request)
    return redirect('login')
