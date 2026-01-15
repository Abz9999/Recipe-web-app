"""Form for user login."""
from django import forms
from django.contrib.auth import authenticate
from recipes.forms.styled_form_mixin import StyledFormMixin


class LogInForm(StyledFormMixin, forms.Form):
    """
    Login form for registered users.

    Fields:
        username: The user's username (starts with @).
        password: The user's password (hidden input).
    """

    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )

    def get_user(self):
        """
        Authenticate the user with the provided credentials.

        Returns:
            The authenticated User object, or None if invalid.
        """
        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user
