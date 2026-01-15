from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from libgravatar import Gravatar


class User(AbstractUser):
    """
    Custom user model with profile info and social features.

    Extends Django's AbstractUser with:
    - Username validation (must start with @)
    - Required first/last name and email
    - Follow/unfollow functionality
    - Favourite recipes functionality
    """

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must start with @ and have at least 3 characters.'
        )],
        help_text='Username must start with @ and have at least 3 characters.'
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""

        return self.gravatar(size=60)

    def follow(self, user):
        """Follow another user."""
        if self != user:
            Follow.objects.get_or_create(follower=self, following=user)

    def unfollow(self, user):
        """Unfollow another user."""
        Follow.objects.filter(follower=self, following=user).delete()

    def is_following(self, user):
        """Check if the user is following another user."""
        return Follow.objects.filter(follower=self, following=user).exists()

    def get_followers(self):
        """Return queryset of users who follow this user."""
        return User.objects.filter(following__following=self)

    def get_following(self):
        """Get a queryset of users this user is following."""
        return User.objects.filter(followers__follower=self)

    def get_followers_count(self):
        """Get the number of followers this user has."""
        return self.get_followers().count()

    def get_following_count(self):
        """Get the number of users this user is following."""
        return self.get_following().count()

    def favourite_recipe(self, recipe):
        """Add a recipe to favourites."""
        from recipes.models.favourite import Favourite
        Favourite.objects.get_or_create(user=self, recipe=recipe)

    def unfavourite_recipe(self, recipe):
        """Remove a recipe from favourites."""
        from recipes.models.favourite import Favourite
        Favourite.objects.filter(user=self, recipe=recipe).delete()

    def has_favourited(self, recipe):
        """Check if user has favourited a recipe."""
        from recipes.models.favourite import Favourite
        return Favourite.objects.filter(user=self, recipe=recipe).exists()

    def get_favourites(self):
        """Get all favourite recipes for this user."""
        from recipes.models.recipe import Recipe
        return Recipe.objects.filter(favourited_by__user=self)

    def get_favourites_count(self):
        """Get count of favourite recipes."""
        return self.favourites.count()


class Follow(models.Model):
    """Model representing a 'follow' relationship between users."""

    follower = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-id']

    def __str__(self):
        """Return a string representation of the follow relationship."""
        return f"{self.follower.username} follows {self.following.username}"

