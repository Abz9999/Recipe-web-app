"""Forms for user profile and account management."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator, ValidationError
from recipes.forms.styled_form_mixin import StyledFormMixin
from recipes.models import User


class UserForm(StyledFormMixin, forms.ModelForm):
    """
    Form for editing user profile information.

    Fields:
        first_name: User's first name.
        last_name: User's last name.
        username: Unique username (starts with @).
        email: User's email address.
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
        }


class NewPasswordMixin(StyledFormMixin, forms.Form):
    """
    Mixin providing password fields with validation.

    Fields:
        new_password: The new password (must contain uppercase, lowercase, number).
        password_confirmation: Must match new_password.
    """

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
                message='Password must contain an uppercase character, '
                        'a lowercase character, and a number.'
            )
        ],
        help_text='Password must contain an uppercase character, '
                  'a lowercase character, and a number'
    )
    password_confirmation = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'})
    )

    def clean(self):
        """Check that password and confirmation match."""
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error(
                'password_confirmation',
                'Confirmation does not match password.'
            )
        return self.cleaned_data


class PasswordForm(NewPasswordMixin):
    """
    Form for changing an existing user's password.

    Fields:
        password: The user's current password (for verification).
        new_password: The new password to set.
        password_confirmation: Confirmation of the new password.
    """

    password = forms.CharField(
        label='Current password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your current password'})
    )

    def __init__(self, user=None, **kwargs):
        """Store the user whose password is changing."""
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Verify the current password is correct."""
        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None and self.user is not None:
            self.add_error('password', "Password is invalid")
        return self.cleaned_data

    def save(self):
        """
        Update the user's password.

        Returns:
            The User object with the updated password.
        """
        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """
    Form enabling new users to register for an account.

    This form extends both `NewPasswordMixin` (for password and confirmation
    fields) and Django's `ModelForm` to create a new `User` instance.
    It validates password strength and matching through the mixin, then
    creates the user with a hashed password using `create_user()`.

    Inherits from:
        NewPasswordMixin: Provides password validation and confirmation fields.
        forms.ModelForm: Generates form fields from the Django User model.

    Fields:
        first_name: User's first name.
        last_name: User's last name.
        username: Unique username (must start with @).
        email: User's email address.
        new_password: Account password.
        password_confirmation: Confirmation of password.
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
        }

    def clean_username(self):
        """Check the username isn't already taken."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                'This username is already taken. Please choose another.'
            )
        return username

    def save(self):
        """
        Create and return a new user account.

        Returns:
            The newly created User object.
        """
        super().save(commit=False)
        return User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )