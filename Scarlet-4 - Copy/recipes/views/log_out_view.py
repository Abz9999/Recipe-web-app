from django.contrib.auth import logout
from django.shortcuts import redirect


def log_out(request):
    """Log out the current user and redirect to the home page."""
    logout(request)
    return redirect('home')
