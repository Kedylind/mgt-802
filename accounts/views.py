"""
Authentication and account views.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import UserRegistrationForm


@require_http_methods(["GET", "POST"])
def signup_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome, {username}!')
                return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def dashboard_view(request):
    """User dashboard view."""
    return render(request, 'accounts/dashboard.html')

