from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View
from recipes.forms import LogInForm
from recipes.views.decorators import LoginProhibitedMixin


class LogInView(LoginProhibitedMixin, View):
    """Handle user login requests."""
    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display the login form."""
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Authenticate and log in the user."""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, "Please correct the errors below.")
            return self.render()
        user = form.get_user()
        if user is not None and getattr(user, 'is_active', True):
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self, form=None):
        """Render log in template with log in form."""
        if form is None:
            form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})
